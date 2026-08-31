// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract AlertLog {
    struct LogRecord {
        uint256 timestamp;
        address sender;
        bool exists;
    }

    mapping(bytes32 => LogRecord) public logs;

    event AlertLogged(bytes32 indexed alertHash, uint256 timestamp, address sender);

    function logAlert(bytes32 alertHash) external {
        require(!logs[alertHash].exists, "Alert already logged");

        logs[alertHash] = LogRecord({
            timestamp: block.timestamp,
            sender: msg.sender,
            exists: true
        });

        emit AlertLogged(alertHash, block.timestamp, msg.sender);
    }

    function verifyAlert(bytes32 alertHash) external view returns (bool, uint256, address) {
        LogRecord memory record = logs[alertHash];
        return (record.exists, record.timestamp, record.sender);
    }
}
