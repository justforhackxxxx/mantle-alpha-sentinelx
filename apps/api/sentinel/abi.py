from __future__ import annotations

def bytes32_from_hex(value: str) -> str:
    normalized = value.removeprefix("0x").lower()
    if len(normalized) != 64:
        raise ValueError("bytes32 value must be 32 bytes")
    int(normalized, 16)
    return normalized


def bytes32_from_text(value: str) -> str:
    return keccak_256(value.encode("utf-8")).hex()


def encode_record_signal_calldata(
    *,
    signal_hash: str,
    agent_id: str,
    signal_type: str,
    target: str,
    horizon: str,
) -> str:
    selector = _selector("recordSignal(bytes32,bytes32,string,string,string)")
    static_args = [
        bytes32_from_hex(signal_hash),
        bytes32_from_text(agent_id),
    ]
    dynamic_args = [
        _encode_string(signal_type),
        _encode_string(target),
        _encode_string(horizon),
    ]
    head_size = 32 * (len(static_args) + len(dynamic_args))
    offsets = []
    cursor = head_size
    for encoded in dynamic_args:
        offsets.append(_uint256(cursor))
        cursor += len(encoded) // 2

    return "0x" + selector + "".join(static_args + offsets + dynamic_args)


def _selector(signature: str) -> str:
    return keccak_256(signature.encode("utf-8")).hex()[:8]


def _encode_string(value: str) -> str:
    raw = value.encode("utf-8")
    padding = (32 - len(raw) % 32) % 32
    return _uint256(len(raw)) + raw.hex() + ("00" * padding)


def _uint256(value: int) -> str:
    if value < 0:
        raise ValueError("uint256 cannot be negative")
    return f"{value:064x}"


def keccak_256(data: bytes) -> bytes:
    rate = 136
    state = [0] * 25
    offset = 0

    while offset + rate <= len(data):
        block = data[offset : offset + rate]
        _absorb_block(state, block)
        _keccak_f1600(state)
        offset += rate

    tail = bytearray(data[offset:])
    tail.append(0x01)
    tail.extend(b"\x00" * (rate - len(tail)))
    tail[-1] ^= 0x80
    _absorb_block(state, bytes(tail))
    _keccak_f1600(state)

    output = bytearray()
    while len(output) < 32:
        for lane in state[: rate // 8]:
            output.extend(lane.to_bytes(8, "little"))
            if len(output) >= 32:
                break
        if len(output) < 32:
            _keccak_f1600(state)
    return bytes(output[:32])


def _absorb_block(state: list[int], block: bytes) -> None:
    for index in range(0, len(block), 8):
        state[index // 8] ^= int.from_bytes(block[index : index + 8], "little")


def _rot(value: int, shift: int) -> int:
    shift %= 64
    return ((value << shift) | (value >> (64 - shift))) & ((1 << 64) - 1)


def _keccak_f1600(state: list[int]) -> None:
    rotation_offsets = [
        [0, 36, 3, 41, 18],
        [1, 44, 10, 45, 2],
        [62, 6, 43, 15, 61],
        [28, 55, 25, 21, 56],
        [27, 20, 39, 8, 14],
    ]
    round_constants = [
        0x0000000000000001,
        0x0000000000008082,
        0x800000000000808A,
        0x8000000080008000,
        0x000000000000808B,
        0x0000000080000001,
        0x8000000080008081,
        0x8000000000008009,
        0x000000000000008A,
        0x0000000000000088,
        0x0000000080008009,
        0x000000008000000A,
        0x000000008000808B,
        0x800000000000008B,
        0x8000000000008089,
        0x8000000000008003,
        0x8000000000008002,
        0x8000000000000080,
        0x000000000000800A,
        0x800000008000000A,
        0x8000000080008081,
        0x8000000000008080,
        0x0000000080000001,
        0x8000000080008008,
    ]
    mask = (1 << 64) - 1

    for constant in round_constants:
        columns = [state[x] ^ state[x + 5] ^ state[x + 10] ^ state[x + 15] ^ state[x + 20] for x in range(5)]
        deltas = [columns[(x - 1) % 5] ^ _rot(columns[(x + 1) % 5], 1) for x in range(5)]
        for x in range(5):
            for y in range(5):
                state[x + 5 * y] ^= deltas[x]

        moved = [0] * 25
        for x in range(5):
            for y in range(5):
                moved[y + 5 * ((2 * x + 3 * y) % 5)] = _rot(state[x + 5 * y], rotation_offsets[x][y])

        for x in range(5):
            for y in range(5):
                state[x + 5 * y] = moved[x + 5 * y] ^ ((~moved[((x + 1) % 5) + 5 * y]) & moved[((x + 2) % 5) + 5 * y])
                state[x + 5 * y] &= mask

        state[0] ^= constant
