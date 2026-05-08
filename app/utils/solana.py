import os
from pathlib import Path
from dotenv import load_dotenv
from solana.rpc.api import Client
from solders.instruction import Instruction, AccountMeta
from solders.pubkey import Pubkey
from solders.solders import VersionedTransaction
from solders.keypair import Keypair
from solders.message import MessageV0
import base58

MEMO_PROGRAM_ID = "MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr"


def record_provenance_on_chain(content_hash: str, ipfs_cid: str) -> str:
    """
    Record provenance on Solana by submitting a Memo Program transaction.

    Returns:
        TxID signature string on success, or "SOLANA_FAILED" if send fails (e.g. insufficient SOL).
    """
    repo_root = Path(__file__).resolve().parents[2]
    load_dotenv(repo_root / ".env")

    rpc_url = os.getenv("SOLANA_RPC_URL")
    private_key_b58 = os.getenv("SOLANA_PRIVATE_KEY")

    if not rpc_url:
        raise RuntimeError("Missing SOLANA_RPC_URL in .env")
    if not private_key_b58:
        raise RuntimeError("Missing SOLANA_PRIVATE_KEY in .env")

    # SOS_PROOF:{content_hash}|{ipfs_cid}
    memo_message = f"SOS_PROOF:{content_hash}|{ipfs_cid}"

    # try:
    #     # Prefer solders' native base58 parsing when available.
    #     from solders.keypair import Keypair  # local import to keep helper lightweight

    #     try:
    #         payer = Keypair.from_base58_string(private_key_b58)
    #     except Exception:
    #         # Fallback: decode base58 secret key bytes and build Keypair from bytes
    #         import base58

    #         secret = base58.b58decode(private_key_b58)
    #         payer = Keypair.from_bytes(secret)

    #     client = Client(rpc_url)
    #     latest = client.get_latest_blockhash()
    #     blockhash = latest.value.blockhash

    #     memo_ix = Instruction(
    #         program_id=Pubkey.from_string(MEMO_PROGRAM_ID),
    #         accounts=[],
    #         data=memo_message.encode("utf-8"),
    #     )

    #     tx = Transaction.new_signed_with_payer(
    #         instructions=[memo_ix],
    #         payer=payer.pubkey(),
    #         signing_keypairs=[payer],
    #         recent_blockhash=blockhash,
    #     )

    #     resp = client.send_transaction(tx, opts=TxOpts(skip_preflight=False))

    #     # solana-py response shape differs across versions
    #     sig = getattr(resp, "value", None) or resp.get("result") if isinstance(resp, dict) else None
    #     if not sig or not isinstance(sig, str):
    #         raise RuntimeError(f"Unexpected send_transaction response: {resp}")

    #     return sig
    # except Exception:
    #     return "SOLANA_FAILED"
    try:
        # Properly decode Keypair
        payer = Keypair.from_base58_string(private_key_b58)
        client = Client(rpc_url)
        
        # 1. Get Blockhash
        res_blockhash = client.get_latest_blockhash()
        blockhash = res_blockhash.value.blockhash

        # 2. Create Instruction
        memo_ix = Instruction(
            program_id=Pubkey.from_string(MEMO_PROGRAM_ID),
            data=memo_message.encode("utf-8"),
            accounts=[] # Memo program doesn't strictly require accounts unless using specific versions
        )

        # 3. Build Modern Transaction
        msg = MessageV0.try_compile(
            payer=payer.pubkey(),
            instructions=[memo_ix],
            address_lookup_table_accounts=[],
            recent_blockhash=blockhash
        )
        
        tx = VersionedTransaction(msg, [payer])

        # 4. Send
        resp = client.send_transaction(tx)
        
        # Return the Signature string
        return str(resp.value)
        
    except Exception as e:
        print(f"DEBUG: Solana error: {e}") # This will tell us the REAL problem
        return "SOLANA_FAILED"


if __name__ == "__main__":
    print("--- SOS Project: solana memo test ---")
    dummy_hash = "deadbeef" * 8  # 64 hex chars
    dummy_cid = "bafybeigdyrzt5dummycidexample"
    txid = record_provenance_on_chain(dummy_hash, dummy_cid)
    print(f"TxID: {txid}")


