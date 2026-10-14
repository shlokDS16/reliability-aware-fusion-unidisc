"""Build the MDLM OpenWebText validation set: last 100,000 documents of the 'train' split ("train[-100000:]", dataloader.py L350-355),
tokenised and wrapped by the OFFICIAL dataloader.get_dataset (GPT-2 tokenizer, eos between docs, blocks of 1022 + BOS/EOS = 1024).

Deviation: datasets.load_dataset('openwebtext', ...) would download all 80 parquet shards (24 GB); the last 100,000 rows all lie in the last
shard (plain_text/train-00079-of-00080.parquet has 100,172 rows, read from its footer), so only that shard (303 MB) was downloaded and
datasets.load_dataset is replaced for this one call by a function returning those last 100,000 rows. Assumes the parquet shards keep the
row order of the original loading script (not verifiable here without the 24 GB download).
"""
import hashlib, sys
from g4_common import *  # noqa
setup_repo_import()
import datasets, pyarrow.parquet as pq, pyarrow.compute as pc, transformers


def main():

    assert OWT_SHARD.exists()
    pf = pq.ParquetFile(str(OWT_SHARD))
    n = pf.metadata.num_rows
    assert n >= 100000
    # keep memory low (commit-limited machine): slice row groups, write the last 100,000 rows to a small parquet, memory-map it
    last_pq = OWT_SHARD.parent / "owt_last100k.parquet"
    if not last_pq.exists():
        tbl = pf.read()
        assert tbl.num_rows == n
        pq.write_table(tbl.slice(n - 100000), str(last_pq)); del tbl
    ds = datasets.Dataset.from_parquet(str(last_pq), cache_dir=str(OWT_SHARD.parent / "arrow_cache"))
    assert len(ds) == 100000
    first_doc, last_doc = ds[0]["text"], ds[len(ds) - 1]["text"]
    info = dict(shard=str(OWT_SHARD), shard_rows=n, n_docs=len(ds), slice=f"rows [{n-100000}, {n}) of shard 79 == train[-100000:]",
                shard_sha256=hashlib.sha256(OWT_SHARD.read_bytes()).hexdigest(),
                first_doc_sha1=hashlib.sha1(first_doc.encode()).hexdigest(), last_doc_sha1=hashlib.sha1(last_doc.encode()).hexdigest(),
                first_doc_head=first_doc[:120], total_chars=int(pc.sum(pc.utf8_length(ds.data.column("text"))).as_py()))
    print(info)

    _real = datasets.load_dataset
    def fake_load_dataset(name, *a, **kw):
        if name == "openwebtext":
            assert kw.get("split") == "train[-100000:]", kw
            return ds
        return _real(name, *a, **kw)
    datasets.load_dataset = fake_load_dataset

    import dataloader
    cfg = make_cfg()
    tok = dataloader.get_tokenizer(cfg)
    OWT_CACHE.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    valid = dataloader.get_dataset(cfg.data.valid, tok, wrap=cfg.data.wrap, mode="validation", cache_dir=cfg.data.cache_dir,
                                   block_size=cfg.model.length, streaming=False, num_proc=1)
    info.update(n_sequences=len(valid), seq_len=int(valid[0]["input_ids"].shape[0]), tokens=len(valid) * 1024, prep_seconds=time.time() - t0,
                tokenizer=cfg.data.tokenizer_name_or_path, bos_id=int(valid[0]["input_ids"][0]), eos_id=int(valid[0]["input_ids"][-1]),
                transformers=transformers.__version__, datasets=datasets.__version__)
    jdump(info, G4 / "t3_data_info.json")
    print(info)


if __name__ == '__main__':
    main()
