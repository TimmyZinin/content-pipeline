"""Publisher Service — thin HTTP wrapper over auto-publisher adapters.
Reads platform_post by ID from DB, publishes via adapter, returns result.
"""
import importlib
import json
import logging
import os
import sys
import traceback
import urllib.request

import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

sys.path.insert(0, "/opt/auto-publisher")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("publisher-service")

app = FastAPI(title="Publisher Service", version="1.0")

DB_CONFIG = {
    "host": os.getenv("PG_HOST", "n8n-postgres"),
    "port": int(os.getenv("PG_PORT", "5432")),
    "dbname": os.getenv("PG_DB", "n8n_production"),
    "user": os.getenv("PG_USER", ""),
    "password": os.getenv("PG_PASSWORD", ""),
}

# Platform name → adapter module name (most are same)
ADAPTER_MAP = {
    "telegram": "telegram",
    "threads_ru": "threads",
    "threads_en": "_publer",  # Via Publer API
    "vk": "vk",
    "bluesky": "bluesky",
    "devto": "devto",
    "hashnode": "hashnode",
    "mastodon": "mastodon",
    "facebook": "_publer",  # Personal profile via Publer
    "tumblr": "tumblr",
    "writeas": "writeas",
    "minds": "minds",
    "nostr": "nostr",
}

# Publer API config
PUBLER_API_KEY = os.getenv("PUBLER_API_KEY", "")
PUBLER_WORKSPACE_ID = os.getenv("PUBLER_WORKSPACE_ID", "")
PUBLER_ACCOUNTS = {
    "threads_en": os.getenv("PUBLER_THREADS_EN_ACCOUNT_ID", ""),
    "facebook": os.getenv("PUBLER_FB_ACCOUNT_ID", ""),
}
# Network names for Publer API
PUBLER_NETWORKS = {
    "threads_en": "threads",
    "facebook": "facebook",
}


def _publer_upload_media(image_url: str) -> str | None:
    """Upload image to Publer via URL, return media_id."""
    upload_url = "https://app.publer.com/api/v1/media/from-url"
    payload = {
        "media": [{"url": image_url, "name": "post_image"}],
        "type": "single",
        "direct_upload": False,
        "in_library": False,
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(upload_url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer-API {PUBLER_API_KEY}")
    req.add_header("Publer-Workspace-Id", PUBLER_WORKSPACE_ID)
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "ContentPipeline/1.0")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())

        # May return job_id for async upload or direct media object
        if "job_id" in result:
            import time
            job_id = result["job_id"]
            for _ in range(12):
                time.sleep(3)
                sreq = urllib.request.Request(f"https://app.publer.com/api/v1/job_status/{job_id}")
                sreq.add_header("Authorization", f"Bearer-API {PUBLER_API_KEY}")
                sreq.add_header("Publer-Workspace-Id", PUBLER_WORKSPACE_ID)
                sreq.add_header("User-Agent", "ContentPipeline/1.0")
                with urllib.request.urlopen(sreq, timeout=15) as sr:
                    status = json.loads(sr.read())
                if status.get("status") == "complete":
                    payload_data = status.get("payload", [])
                    if payload_data and isinstance(payload_data, list):
                        media_obj = payload_data[0] if isinstance(payload_data[0], dict) else {}
                        return media_obj.get("id", "")
                    return None
            return None
        elif "id" in result:
            return result["id"]
        return None
    except Exception as e:
        log.error(f"Publer media upload failed: {e}")
        return None


def _publish_via_publer(platform: str, text: str, image_url: str | None = None) -> dict:
    """Publish via Publer API. Async: returns job_id, then polls for result."""
    account_id = PUBLER_ACCOUNTS.get(platform, "")
    network = PUBLER_NETWORKS.get(platform, "")
    if not PUBLER_API_KEY or not account_id or not network:
        return {"ok": False, "error": f"Publer config missing for {platform}"}

    # Step 1: Upload media if image provided
    media_id = None
    if image_url:
        log.info(f"Publer: uploading media from {image_url[:60]}...")
        media_id = _publer_upload_media(image_url)
        if media_id:
            log.info(f"Publer: media uploaded, id={media_id}")
        else:
            log.warning("Publer: media upload failed, publishing text-only")

    # Step 2: Compose post
    url = "https://app.publer.com/api/v1/posts/schedule/publish"
    post_type = "photo" if media_id else "status"
    network_data = {"type": post_type, "text": text}
    if media_id:
        network_data["media"] = [{"id": media_id, "type": "image"}]

    post_entry = {
        "networks": {network: network_data},
        "accounts": [{"id": account_id}],
    }

    body = json.dumps({"bulk": {"state": "now", "posts": [post_entry]}}).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Authorization", f"Bearer-API {PUBLER_API_KEY}")
    req.add_header("Publer-Workspace-Id", PUBLER_WORKSPACE_ID)
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "ContentPipeline/1.0")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())

        job_id = result.get("job_id", "")
        if not job_id:
            return {"ok": False, "error": f"No job_id: {result}"}

        # Poll for completion (max 60s)
        import time
        for _ in range(12):
            time.sleep(5)
            status_url = f"https://app.publer.com/api/v1/job_status/{job_id}"
            sreq = urllib.request.Request(status_url)
            sreq.add_header("Authorization", f"Bearer-API {PUBLER_API_KEY}")
            sreq.add_header("Publer-Workspace-Id", PUBLER_WORKSPACE_ID)
            sreq.add_header("User-Agent", "ContentPipeline/1.0")
            with urllib.request.urlopen(sreq, timeout=15) as sr:
                status = json.loads(sr.read())
            if status.get("status") == "complete":
                payload = status.get("payload", [{}])
                post = payload[0].get("post", {}) if payload else {}
                post_link = post.get("post_link", "")
                return {"ok": True, "post_id": post_link or job_id}
            elif status.get("status") == "error":
                return {"ok": False, "error": f"Publer job failed: {status}"}

        return {"ok": False, "error": f"Publer job timeout (60s), job_id={job_id}"}

    except Exception as e:
        return {"ok": False, "error": str(e)}


class PublishRequest(BaseModel):
    platform_post_id: int


class PublishResult(BaseModel):
    status: str  # "ok" or "error"
    platform: str
    post_id: int
    external_id: str | None = None
    error: str | None = None


def get_db():
    return psycopg2.connect(**DB_CONFIG)


def get_post(post_id: int) -> dict | None:
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT pp.id, pp.post_id, pp.platform, pp.adapted_text,
                   pp.comment_text, pp.reply_text, pp.link_url, pp.link_placement,
                   pp.include_image, pp.image_url, pp.status, pp.retries,
                   pp.post_external_id,
                   p.product_url, p.product_name, p.post_text
            FROM content.platform_posts pp
            JOIN content.posts p ON p.id = pp.post_id
            WHERE pp.id = %s
        """, (post_id,))
        row = cur.fetchone()
        if not row:
            return None
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))
    finally:
        conn.close()


def publish_one(post: dict) -> PublishResult:
    platform = post["platform"]
    adapter_name = ADAPTER_MAP.get(platform)
    if not adapter_name:
        return PublishResult(status="error", platform=platform, post_id=post["id"],
                             error=f"No adapter for: {platform}")

    # Publer path
    if adapter_name == "_publer":
        text = post["adapted_text"] or ""
        image_url = post.get("image_url") if post.get("include_image") else None
        result = _publish_via_publer(platform, text, image_url)
        if isinstance(result, dict):
            ok = result.get("ok", False)
            return PublishResult(
                status="ok" if ok else "error",
                platform=platform, post_id=post["id"],
                external_id=str(result.get("post_id", "")) if ok else None,
                error=result.get("error") if not ok else None
            )
        return PublishResult(status="ok", platform=platform, post_id=post["id"])

    try:
        mod = importlib.import_module(f"adapters.{adapter_name}")
        fn = mod.publish
    except Exception as e:
        return PublishResult(status="error", platform=platform, post_id=post["id"],
                             error=f"Import failed: {e}")

    text = post["adapted_text"] or ""
    link_url = post.get("link_url") or ""
    link_placement = post.get("link_placement") or "none"
    kwargs = {}

    if post.get("image_url") and post.get("include_image"):
        kwargs["image_url"] = post["image_url"]

    # Strategy-aware link propagation
    # Char limits for short-form platforms
    CHAR_LIMITS = {"bluesky": 300, "nostr": 300}

    if link_url and link_placement == "body":
        if platform == "telegram":
            # HTML anchor (s04: no bare URLs)
            if link_url not in text:
                product = post.get("product_name") or "Link"
                text = text.rstrip() + f'\n\n<a href="{link_url}">{product}</a>'

        elif platform in ("devto", "hashnode"):
            # Markdown CTA block for long-form articles
            if link_url not in text:
                product = post.get("product_name") or "Source"
                text = text.rstrip() + f"\n\n---\n\n**Read more:** [{product}]({link_url})"

        elif platform in ("bluesky", "nostr"):
            # Short-form: only add URL if it fits within char limit
            limit = CHAR_LIMITS.get(platform, 300)
            url_addition = "\n\n" + link_url
            if link_url not in text and len(text) + len(url_addition) <= limit:
                text = text.rstrip() + url_addition

        elif platform in ("vk", "mastodon", "writeas", "minds"):
            # Simple append (no char limit issues)
            if link_url not in text:
                text = text.rstrip() + "\n\n" + link_url

    if link_url and link_placement == "comment":
        # LinkedIn, Facebook: link goes in comment_text
        comment = post.get("comment_text") or ""
        if link_url not in comment:
            comment = (comment + "\n\n" + link_url).strip() if comment else link_url
        kwargs["comment_text"] = comment

    if link_url and link_placement == "reply":
        # Threads: link goes in reply_text
        reply = post.get("reply_text") or ""
        if link_url not in reply:
            reply = (reply + "\n\n" + link_url).strip() if reply else link_url
        kwargs["reply_text"] = reply

    # Pass through comment/reply even without link
    if post.get("comment_text") and "comment_text" not in kwargs:
        kwargs["comment_text"] = post["comment_text"]
    if post.get("reply_text") and "reply_text" not in kwargs:
        kwargs["reply_text"] = post["reply_text"]

    # For devto/hashnode: extract title from first markdown heading or use product_name
    if platform in ("devto", "hashnode"):
        lines = text.split("\n")
        title = post.get("product_name", "Post")
        for line in lines:
            if line.startswith("# "):
                title = line[2:].strip()
                break
        kwargs["title"] = title

    try:
        result = fn(text, **kwargs)
    except Exception as e:
        log.error(f"Adapter error: {platform} post={post['id']}: {traceback.format_exc()}")
        return PublishResult(status="error", platform=platform, post_id=post["id"],
                             error=f"{type(e).__name__}: {str(e)[:200]}")

    # Normalize adapter response
    if isinstance(result, dict):
        ok = result.get("ok", result.get("status") == "ok")
        ext_id = str(result.get("post_id", result.get("id", ""))) if ok else None
        error = None if ok else result.get("error", result.get("reason", str(result)[:200]))

        # Phase 2A: Threads RU reply after main post (feature flag)
        if ok and platform == "threads_ru" and THREADS_REPLY_ENABLED and ext_id:
            reply_text = kwargs.get("reply_text") or post.get("reply_text") or ""
            if reply_text:
                log.info(f"Threads reply: posting reply to {ext_id}")
                reply_result = _threads_create_reply(ext_id, reply_text)
                if reply_result.get("ok"):
                    log.info(f"Threads reply ok: {reply_result.get('reply_id')}")
                else:
                    log.warning(f"Threads reply failed: {reply_result.get('error')}")
                    # Reply failure doesn't fail the main post

        return PublishResult(
            status="ok" if ok else "error",
            platform=platform, post_id=post["id"],
            external_id=ext_id, error=error
        )

    return PublishResult(status="ok", platform=platform, post_id=post["id"],
                         external_id=str(result) if result else None)


# Staged rollout: only these platforms are allowed to publish
# Add platforms here as they pass verification
PUBLISH_ALLOWLIST = [p.strip() for p in os.getenv("PUBLISH_ALLOWLIST", "telegram,writeas,minds").split(",") if p.strip()]


def _update_post_status(post_id: int, status: str, external_id: str | None = None,
                        error: str | None = None, retries: int | None = None) -> None:
    """Update platform_post status in DB. Publisher Service = owner of status transitions."""
    conn = get_db()
    try:
        cur = conn.cursor()
        if status == "sent":
            cur.execute(
                "UPDATE content.platform_posts SET status = 'sent', post_external_id = %s, published_at = NOW(), error = NULL WHERE id = %s;",
                (external_id or "", post_id)
            )
        elif status == "failed":
            safe_error = (error or "unknown")[:500].replace("'", "''")
            cur.execute(
                "UPDATE content.platform_posts SET status = 'failed', error = %s, retries = COALESCE(retries, 0) + 1 WHERE id = %s;",
                (safe_error, post_id)
            )
        conn.commit()
    except Exception as e:
        log.error(f"DB update failed for post {post_id}: {e}")
        conn.rollback()
    finally:
        conn.close()


@app.post("/publish", response_model=PublishResult)
def publish_endpoint(req: PublishRequest):
    post = get_post(req.platform_post_id)
    if not post:
        raise HTTPException(404, f"platform_post {req.platform_post_id} not found")
    if post["platform"] not in PUBLISH_ALLOWLIST:
        raise HTTPException(403, f"ROLLOUT GUARD: platform '{post['platform']}' not in allowlist {PUBLISH_ALLOWLIST}")
    if post["status"] not in ("scheduled", "failed"):
        raise HTTPException(400, f"DUPLICATE GUARD: status='{post['status']}', refusing to publish. Only 'scheduled' or 'failed' accepted.")

    # Atomic lock: claim the post by setting status='sending' to prevent race conditions
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE content.platform_posts SET status = 'sending' WHERE id = %s AND status IN ('scheduled', 'failed') RETURNING id;",
            (req.platform_post_id,)
        )
        claimed = cur.fetchone()
        conn.commit()
        if not claimed:
            raise HTTPException(409, f"DUPLICATE GUARD: post {req.platform_post_id} already claimed by another process")
    finally:
        conn.close()

    log.info(f"Publishing: id={post['id']} platform={post['platform']}")
    result = publish_one(post)
    log.info(f"Result: {result.status} {result.platform} ext={result.external_id} err={result.error}")

    # Publisher Service = owner of final status transition
    if result.status == "ok":
        _update_post_status(req.platform_post_id, "sent", external_id=result.external_id)
    else:
        _update_post_status(req.platform_post_id, "failed", error=result.error)

    return result


class VerifyRequest(BaseModel):
    platform_post_id: int


class VerifyResult(BaseModel):
    status: str  # "verified" or "unverified" or "error"
    platform: str
    post_id: int
    reason: str | None = None


def verify_one(post: dict) -> VerifyResult:
    """Check if post actually exists on the platform."""
    platform = post["platform"]
    ext_id = post.get("post_external_id", "")

    if not ext_id:
        return VerifyResult(status="unverified", platform=platform, post_id=post["id"],
                            reason="no external_id")

    try:
        if platform == "telegram":
            # TG: forward message to check existence not practical without admin
            # Trust external_id from sendMessage response
            return VerifyResult(status="verified", platform=platform, post_id=post["id"],
                                reason="sendMessage response trusted")

        elif platform == "devto":
            url = f"https://dev.to/api/articles/{ext_id}"
            req = urllib.request.Request(url, method="GET")
            req.add_header("api-key", os.getenv("DEVTO_API_KEY", ""))
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
            if data.get("id"):
                return VerifyResult(status="verified", platform=platform, post_id=post["id"])

        elif platform == "vk":
            token = os.getenv("VK_USER_TOKEN", "")
            group_id = os.getenv("VK_GROUP_ID", "")
            url = f"https://api.vk.com/method/wall.getById?posts=-{group_id}_{ext_id}&access_token={token}&v=5.199"
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read())
            items = data.get("response", {}).get("items", [])
            if items:
                return VerifyResult(status="verified", platform=platform, post_id=post["id"])

        elif platform == "threads_ru":
            token = os.getenv("THREADS_ACCESS_TOKEN", "")
            url = f"https://graph.threads.net/v1.0/{ext_id}?fields=id,text&access_token={token}"
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read())
            if data.get("id"):
                return VerifyResult(status="verified", platform=platform, post_id=post["id"])

        elif platform == "hashnode":
            # Hashnode: GraphQL query by publication ID
            return VerifyResult(status="verified", platform=platform, post_id=post["id"],
                                reason="GraphQL post creation response trusted")

        elif platform == "bluesky":
            # Bluesky: AT URI from createRecord response
            return VerifyResult(status="verified", platform=platform, post_id=post["id"],
                                reason="createRecord response trusted")

        return VerifyResult(status="unverified", platform=platform, post_id=post["id"],
                            reason=f"no verify logic for {platform}")

    except Exception as e:
        return VerifyResult(status="error", platform=platform, post_id=post["id"],
                            reason=f"{type(e).__name__}: {str(e)[:100]}")


@app.post("/verify", response_model=VerifyResult)
def verify_endpoint(req: VerifyRequest):
    post = get_post(req.platform_post_id)
    if not post:
        raise HTTPException(404, f"platform_post {req.platform_post_id} not found")
    if post["status"] != "sent":
        raise HTTPException(400, f"Status '{post['status']}', expected 'sent'")

    result = verify_one(post)
    log.info(f"Verify: {result.status} {result.platform} post={result.post_id} reason={result.reason}")
    return result


class TestPublishRequest(BaseModel):
    platform: str
    text: str = "Safe test post from Publisher Service. Please ignore."
    image_url: str | None = None


@app.post("/test-publish", response_model=PublishResult)
def test_publish_endpoint(req: TestPublishRequest):
    """DISABLED. Was publishing to real accounts. Use local testing only."""
    raise HTTPException(403, "DISABLED: /test-publish publishes to real accounts. Not safe for prod. Use local adapter testing instead.")
    fake_post = {
        "id": 0,
        "post_id": 0,
        "platform": req.platform,
        "adapted_text": req.text,
        "comment_text": None,
        "reply_text": None,
        "link_url": None,
        "link_placement": "none",
        "include_image": bool(req.image_url),
        "image_url": req.image_url,
        "status": "test",
        "retries": 0,
        "post_external_id": None,
        "product_url": None,
        "product_name": None,
        "post_text": req.text,
    }
    log.info(f"TEST publish: platform={req.platform} (no DB changes)")
    result = publish_one(fake_post)
    log.info(f"TEST result: {result.status} {result.platform} ext={result.external_id}")
    return result


# Feature flags
THREADS_REPLY_ENABLED = os.getenv("THREADS_REPLY_ENABLED", "false").lower() == "true"

# Threads RU constants (from adapters/threads.py)
THREADS_TOKEN = os.getenv("THREADS_ACCESS_TOKEN", "")
THREADS_USER_ID = os.getenv("THREADS_USER_ID", "")
THREADS_API = "https://graph.threads.net/v1.0"


def _threads_create_reply(parent_post_id: str, reply_text: str) -> dict:
    """Create a reply to a Threads post. Returns {ok, reply_id} or {ok: false, error}."""
    if not THREADS_TOKEN or not THREADS_USER_ID:
        return {"ok": False, "error": "THREADS credentials not set"}

    try:
        import time as _time

        # Step 1: Create reply container
        params = {
            "media_type": "TEXT",
            "text": reply_text[:500],
            "reply_to_id": parent_post_id,
            "access_token": THREADS_TOKEN,
        }
        url = f"{THREADS_API}/{THREADS_USER_ID}/threads"
        data = urllib.parse.urlencode(params).encode()
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())

        container_id = result.get("id")
        if not container_id:
            return {"ok": False, "error": f"No reply container: {result}"}

        # Step 2: Wait for processing
        _time.sleep(5)

        # Step 3: Publish reply
        pub_params = {
            "creation_id": container_id,
            "access_token": THREADS_TOKEN,
        }
        pub_url = f"{THREADS_API}/{THREADS_USER_ID}/threads_publish"
        pub_data = urllib.parse.urlencode(pub_params).encode()
        pub_req = urllib.request.Request(pub_url, data=pub_data, method="POST")
        with urllib.request.urlopen(pub_req, timeout=30) as resp:
            pub_result = json.loads(resp.read())

        reply_id = pub_result.get("id", "")
        log.info(f"Threads reply published: {reply_id} (parent: {parent_post_id})")
        return {"ok": True, "reply_id": reply_id}

    except Exception as e:
        log.error(f"Threads reply failed: {e}")
        return {"ok": False, "error": str(e)}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "threads_reply_enabled": THREADS_REPLY_ENABLED,
        "publish_allowlist": PUBLISH_ALLOWLIST,
    }
