vcl 4.1;

import std;

backend default {
    .host = "minio";           
    .port = "9000";
    .connect_timeout = 5s;
    .first_byte_timeout = 30s;
    .between_bytes_timeout = 10s;
}

sub vcl_recv {
    # Only cache GET and HEAD requests
    if (req.method != "GET" && req.method != "HEAD") {
        return (pass);
    }

    # Optional: bypass cache for certain paths (e.g., /upload endpoint if any)
    if (req.url ~ "^/upload" || req.url ~ "^/api/") {
        return (pass);
    }

    # For presigned URLs: they have long query strings → normalize for caching
    # (Varnish caches based on full URL by default, including query → good for unique presigned links)
    # If you want to ignore signature parts, you can unset req.url.query here (advanced)

    # Strip cookies for static/image requests (profile pics usually don't need cookies)
    if (req.url ~ "\.(jpg|jpeg|png|webp|gif|ico|svg|css|js)$" ||
        req.url ~ "X-Amz-") {   # presigned URLs often have these params
        unset req.http.Cookie;
    }

    return (hash);
}

sub vcl_backend_response {
    # Cache images/static for a long time (override MinIO if needed)
    if (bereq.url ~ "\.(jpg|jpeg|png|webp|gif)$" || bereq.url ~ "X-Amz-") {
        set beresp.ttl = 24h;           # cache 1 day
        set beresp.grace = 1h;          # serve stale while revalidating
    }

    # If MinIO sets Cache-Control, respect it (good default)
    # But you can force longer TTLs here if desired

    # Debug header
    if (beresp.http.X-Cache == "") {
        set beresp.http.X-Cache = "MISS";
    }
}

sub vcl_deliver {
    # Add cache hit/miss header for debugging
    if (obj.hits > 0) {
        set resp.http.X-Cache = "HIT (" + obj.hits + ")";
    } else {
        set resp.http.X-Cache = "MISS";
    }

    # Optional: remove some headers for cleaner responses
    unset resp.http.Via;
    unset resp.http.X-Varnish;
}