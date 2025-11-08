import logging
import logging.handlers
import time
import os

from threading import Thread
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import can
# import ntplib # pooisbly not needed as RPi will get time from ntp on boot

###############################################



def my_app():
        pass
        #print("I got here!")

class FTPThread(Thread):
    def __init__(self, host, port, username, password, directory):
        super().__init__()
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.directory = directory
        self.server = None

    def run(self):
        # Instantiate a dummy authorizer for managing 'virtual' users
        authorizer = DummyAuthorizer()

        # Add a user with full permissions
        authorizer.add_user(self.username, self.password, self.directory, perm='elradfmw')

        # Instantiate FTP handler class
        handler = FTPHandler
        handler.authorizer = authorizer

        # Define the FTP server
        self.server = FTPServer((self.host, self.port), handler)

        # Start the FTP server
        print(f"Starting FTP server on {self.host}:{self.port} in a separate thread...")
        self.server.serve_forever()

    def stop(self):
        if self.server:
            print("Stopping FTP server...")
            self.server.close_all()
################################################
# Configure the logger
logger = logging.getLogger('power_logger')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('power.log')

# Create a TimedRotatingFileHandler
# This handler will rotate the log file every day at midnight.
# 'when'='midnight' specifies the rotation time.
# 'interval'=1 specifies the rotation interval (e.g., 1 day).
# 'backupCount'=7 keeps the last 7 rotated log files.
th = logging.handlers.TimedRotatingFileHandler(
    filename='power.log',
    when='midnight',
    interval=1,
    backupCount=7
)

# Define and set formatter with clean timestamp
formatter = logging.Formatter(
    fmt="%(asctime)s - %(levelname)s - %(name)s - %(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
fh.setFormatter(formatter)
th.setFormatter(formatter)
# Add the handler to the logger
logger.addHandler(fh)
logger.addHandler(th)

################# main() ##########################################
if __name__ == "__main__":
    # Configuration for the FTP server
    FTP_HOST = '10.42.0.2'
    FTP_PORT = 2121  # Use a non-privileged port for testing
    FTP_USER = 'doug'
    FTP_PASS = 'qwert!!'
    #FTP_DIR = os.path.join(os.getcwd(), 'ftp_root') # Create an 'ftp_root' directory in current working directory
    FTP_DIR = os.getcwd()
    # Create the directory if it doesn't exist
    #os.makedirs(FTP_DIR, exist_ok=True)

    # Create and start the FTP server in a separate thread
    ftp_server_thread = FTPThread(FTP_HOST, FTP_PORT, FTP_USER, FTP_PASS, FTP_DIR)
    ftp_server_thread.start()

    # Main application can continue running here
    print("Main application is running...")
    # Log some messages
    logger.info("Application started.")
    logger.warning("This is a warning message.")
    logger.error("An error occurred!")

    # Simulate application running for a while
    try:
        while True:
            print("Logging messages. Check 'power.log' for output.")
            print("The log file will rotate daily at midnight.")
            logger.info("Application Running.")
            my_app()
            time.sleep(60)
    except KeyboardInterrupt:
        pass
            # You can perform other tasks here while the FTP server runs in the background

            # To stop the FTP server gracefully (e.g., on program exit)
    try:
        input("Press Enter to stop the FTP server and exit...\n")
    except KeyboardInterrupt:
        pass
    finally:
        ftp_server_thread.stop()
        ftp_server_thread.join() # Wait for the thread to finish
        print("FTP server stopped and application exited.")
    
    