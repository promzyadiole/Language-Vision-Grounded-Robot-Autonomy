from __future__ import annotations

import math
from typing import Any

import rclpy
from geometry_msgs.msg import PoseWithCovarianceStamped
from rclpy.node import Node


def yaw_to_quaternion(yaw: float) -> tuple[float, float, float, float]:
    half = yaw / 2.0
    return 0.0, 0.0, math.sin(half), math.cos(half)


class InitialPosePublisher(Node):
    def __init__(self) -> None:
        super().__init__("initial_pose_publisher")
        self.publisher = self.create_publisher(PoseWithCovarianceStamped, "/initialpose", 10)

    def publish_initial_pose(
        self,
        x: float,
        y: float,
        yaw: float,
        cov_x: float = 0.1,
        cov_y: float = 0.1,
        cov_yaw: float = 0.03,
    ) -> dict[str, Any]:
        msg = PoseWithCovarianceStamped()
        msg.header.frame_id = "map"
        msg.header.stamp = self.get_clock().now().to_msg()

        _, _, qz, qw = yaw_to_quaternion(yaw)
        msg.pose.pose.position.x = x
        msg.pose.pose.position.y = y
        msg.pose.pose.position.z = 0.0
        msg.pose.pose.orientation.z = qz
        msg.pose.pose.orientation.w = qw

        msg.pose.covariance[0] = cov_x
        msg.pose.covariance[7] = cov_y
        msg.pose.covariance[35] = cov_yaw

        self.publisher.publish(msg)
        return {
            "success": True,
            "message": "Initial pose published.",
            "pose": {"x": x, "y": y, "yaw": yaw},
        }


_initial_pose_node: InitialPosePublisher | None = None


def get_initial_pose_publisher() -> InitialPosePublisher:
    global _initial_pose_node
    if _initial_pose_node is None:
        if not rclpy.ok():
            rclpy.init()
        _initial_pose_node = InitialPosePublisher()
    return _initial_pose_node