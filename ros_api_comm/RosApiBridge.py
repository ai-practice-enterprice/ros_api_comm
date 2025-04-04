# of course we import the most import library 
import rclpy
import rclpy.executors
from rclpy.node import Node
from rclpy.duration import Duration
# i can create these with the Node module but this is just for pylance to detect typing
from rclpy.publisher import Publisher
from rclpy.subscription import Subscription 

from geometry_msgs.msg import PoseStamped

# https://index.ros.org/p/nav2_simple_commander/
# https://automaticaddison.com/how-to-send-a-goal-path-to-the-ros-2-navigation-stack-nav2/
# https://docs.nav2.org/commander_api/index.html
# https://github.com/ros-navigation/navigation2/blob/main/nav2_simple_commander/nav2_simple_commander/example_waypoint_follower.py
from nav2_simple_commander.robot_navigator import BasicNavigator , TaskResult

# other libraries
from http.server import BaseHTTPRequestHandler , HTTPServer
from queue import Queue
import threading
import asyncio
import httpx
import time
import json
import urllib.parse

from typing import Dict


# https://www.youtube.com/watch?v=LlRJBtHLzu4&ab_channel=RoboticsBack-End
# https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html
# https://docs.ros.org/en/foxy/Tutorials/Intermediate/Writing-an-Action-Server-Client/Py.html

# https://realpython.com/python-thread-lock/
http_queue_condition = threading.Condition() 

# ROS API BRIDGE ===============================================================================================
# NOTE: RosApiBridge is a ROS node in itself but acts more like 
# a topic distributor to send and receive different types of communication messages
class RosApiBridge(Node):
    def __init__(self):
        super().__init__("ros_api_bridge")
        # the moment rclpy.spin is executed on this node (so this -> rclpy.spin(thisNode))
        # then this node's callback functions will be executed every time_callback_sec's        
        self.process_request_caller = self.create_timer(
            timer_period_sec=0.5,
            callback=self.process_requests_in_queue
        )

        self.http_request_queue = Queue()
        self.get_logger().info("RosApiBridge node started")

    def process_requests_in_queue(self):

        while not self.http_request_queue.empty():
            request = self.http_request_queue.get()

  
    
    async def create(self, namespace: str, topic: str, poses: list[float]):
        full_topic = namespace + "/" + topic
        
        self.get_logger().info(f"created publisher on topic {topic} in namespace {namespace}")

        if topic == "":
            pass
        else:
            self.get_logger().error(f"Unknown topic: {topic}")
            return False


# HTTP HANDLER ===============================================================================================
class HttpHandler(BaseHTTPRequestHandler):

    def __init__(self,ros_node, request, client_address, server):
        super().__init__(request, client_address, server)
        self.ros_node: RosApiBridge = ros_node

    def do_GET(self):
        query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)        
        request = {
            "namespace" : "",
            "message" : "",
            "topic" : "",
        }
        request["namespace"] = query_components.get("namespace", "")[0]
        request["message"] = query_components.get("message", "")[0]
        request["topic"] = query_components.get("topic", "")[0]
        
        # of course we validate the request first we don't want empty messages or topics for example
        # CHECKING REQUEST ===============================================================
        if not all(request):
            message = f"some parts of the request are empty : {request}"
            self.send_response(
                code=400,
                message=message
            )
            return
        # CHECKING REQUEST ===============================================================
        
        # adding the request to the queue
        with http_queue_condition:
            self.ros_node.http_request_queue.put(request)

        self.send_response(
            code=200,
            message="created node"
        )



# MAIN PROGRAM ===============================================================================================

def run_http_server(ros_node: RosApiBridge,url:str = "http://bsu-api-server", port: int = 8003):
    server_address = (url, port)
    
    http_handler = HttpHandler(ros_node)
    http_server = HTTPServer(server_address, http_handler)
    
    print(f"Starting http server listening to {url} on port {port}")

    http_server.serve_forever()


# instead of shutting down the node each time
# we create a dictionary of nodes each shutting down at their own time
# which is different from here: https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html
def main(args=None):
    rclpy.init(args=args)

    bridgeNode = RosApiBridge()
     
    # the http server is started on a different thread to keep the main program running
    http_thread = threading.Thread(target=run_http_server, args=(bridgeNode,"http://bsu-api-server",8003),daemon=False)
    http_thread.start()

    # spin already implements a while loop
    rclpy.spin(bridgeNode)

    # if the RosApiBridge is shutdown then the thread needs to be shutdown as well
    rclpy.shutdown()
    http_thread.join()

if __name__ == "__main__":
    main()

