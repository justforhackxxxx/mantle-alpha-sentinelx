// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract SignalRegistry {
    enum Outcome {
        Pending,
        Hit,
        Miss,
        Invalid
    }

    struct SignalRecord {
        bytes32 signalHash;
        bytes32 agentId;
        string signalType;
        string target;
        string horizon;
        uint256 createdAt;
        Outcome outcome;
        uint256 resolvedAt;
    }

    mapping(bytes32 => SignalRecord) public signals;
    bytes32[] public signalHashes;

    event SignalRecorded(
        bytes32 indexed signalHash,
        bytes32 indexed agentId,
        string signalType,
        string target,
        string horizon,
        uint256 createdAt
    );

    event SignalOutcomeResolved(
        bytes32 indexed signalHash,
        Outcome outcome,
        uint256 resolvedAt
    );

    function recordSignal(
        bytes32 signalHash,
        bytes32 agentId,
        string calldata signalType,
        string calldata target,
        string calldata horizon
    ) external {
        require(signalHash != bytes32(0), "empty signal hash");
        require(signals[signalHash].createdAt == 0, "signal exists");

        signals[signalHash] = SignalRecord({
            signalHash: signalHash,
            agentId: agentId,
            signalType: signalType,
            target: target,
            horizon: horizon,
            createdAt: block.timestamp,
            outcome: Outcome.Pending,
            resolvedAt: 0
        });
        signalHashes.push(signalHash);

        emit SignalRecorded(signalHash, agentId, signalType, target, horizon, block.timestamp);
    }

    function resolveOutcome(bytes32 signalHash, Outcome outcome) external {
        SignalRecord storage record = signals[signalHash];
        require(record.createdAt != 0, "unknown signal");
        require(record.outcome == Outcome.Pending, "already resolved");
        require(outcome != Outcome.Pending, "invalid outcome");

        record.outcome = outcome;
        record.resolvedAt = block.timestamp;

        emit SignalOutcomeResolved(signalHash, outcome, block.timestamp);
    }

    function signalCount() external view returns (uint256) {
        return signalHashes.length;
    }
}

