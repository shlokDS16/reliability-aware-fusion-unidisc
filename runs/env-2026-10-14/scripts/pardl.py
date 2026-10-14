"""Resumable multi-connection downloader (the link gives ~0.1-0.3 MB/s per connection, more with parallel ranges).
usage: python pardl.py URL OUT [connections=16] [chunk_mb=16]"""
import sys, os, time, threading, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

url, out = sys.argv[1], sys.argv[2]
nconn = int(sys.argv[3]) if len(sys.argv) > 3 else 16
chunk = (int(sys.argv[4]) if len(sys.argv) > 4 else 16) * 1024 * 1024


def head(u):
    req = urllib.request.Request(u, method="HEAD")
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.geturl(), int(r.headers["Content-Length"])


final_url, size = head(url)
resolved_at = [time.time()]
print("size", size, "url", final_url[:90], flush=True)
nchunks = (size + chunk - 1) // chunk
part_dir = out + ".parts"; os.makedirs(part_dir, exist_ok=True)
done = [os.path.exists(f"{part_dir}/{i}") and os.path.getsize(f"{part_dir}/{i}") == min(chunk, size - i * chunk) for i in range(nchunks)]
lock = threading.Lock(); got = [sum(min(chunk, size - i * chunk) for i in range(nchunks) if done[i])]; t0 = time.time(); base = got[0]


def fetch(i):
    if done[i]:
        return
    s = i * chunk; e = min(size, s + chunk) - 1
    global final_url
    for attempt in range(80):
        try:
            if time.time() - resolved_at[0] > 900:  # presigned CDN links expire: re-resolve every 15 min
                with lock:
                    if time.time() - resolved_at[0] > 900:
                        final_url, _ = head(url); resolved_at[0] = time.time()
            req = urllib.request.Request(final_url, headers={"Range": f"bytes={s}-{e}"})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            if len(data) != e - s + 1:
                raise IOError("short read")
            with open(f"{part_dir}/{i}.tmp", "wb") as f:
                f.write(data)
            os.replace(f"{part_dir}/{i}.tmp", f"{part_dir}/{i}")
            with lock:
                got[0] += len(data)
            return
        except Exception as ex:
            time.sleep(min(30, 2 + attempt))
    raise RuntimeError(f"chunk {i} failed")


def report():
    while got[0] < size:
        time.sleep(30)
        print(f"{got[0]/1e6:.0f}/{size/1e6:.0f} MB, {(got[0]-base)/(time.time()-t0)/1e6:.2f} MB/s", flush=True)


threading.Thread(target=report, daemon=True).start()
with ThreadPoolExecutor(nconn) as ex:
    list(ex.map(fetch, range(nchunks)))
with open(out, "wb") as f:
    for i in range(nchunks):
        with open(f"{part_dir}/{i}", "rb") as p:
            f.write(p.read())
import shutil; shutil.rmtree(part_dir)
print("done", out, os.path.getsize(out), flush=True)
