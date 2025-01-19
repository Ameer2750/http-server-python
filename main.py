import os
import socket
import logging

logging.basicConfig(
    filename="server.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def get_content_type(file_path):
    if file_path.endswith(".html"):
        return "text/html"
    elif file_path.endswith(".css"):
        return "text/css"
    elif file_path.endswith(".jpg") or file_path.endswith(".jpeg"):
        return "text/jpeg"
    elif file_path.endswith(".png"):
        return "image/png"
    else: 
        return "application/octet-stream"


class SimpleHttpServer:
    def __init__(self, host= '127.0.0.1', port=8888, static_dir="static"):
        self.host = host
        self.port = port
        self.static_dir = static_dir
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()    
    
    
    def start(self):
        logging.info(f"Server running on http://{self.host}:{self.port}")

        while True:
            client_socket, client_address =  self.server_socket.accept()
            
            request = client_socket.recv(1024)
            request_str = request.decode('utf-8')
            request_lines = request_str.split("\r\n")
            request_line = request_lines[0];
            parts = request_line.split(' ')
            method = parts[0];
            path = parts[1];
            
            logging.info(f"Request Method: {method}, Path: {path}")

            file_name = path.lstrip('/')
           
            if file_name == '':
                file_name = 'index.html'
                
            file_path = os.path.join(self.static_dir, file_name)
            logging.info(f"Requested file: {file_path}")

            
            # Check if the requested path is a directory
            if os.path.isdir(file_path):
                file_list = os.listdir(file_path)
                html_content = "<ul>"
                for file in file_list:
                    html_content += f"<li><a href='{file}'>{file}</a></li>"
                html_content += "</ul>"
                
                # Prepare the response for directory listing
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{html_content}".encode('utf-8')

            elif os.path.exists(file_path):  # File exists
                with open(file_path, 'rb') as file:
                    file_content = file.read()
                
                content_type = get_content_type(file_path)
                content_length = len(file_content)
                
                # Prepare the response for the requested file
                headers = f"Content-Type: {content_type}\r\n"
                headers += f"Content-Length: {content_length}\r\n"
                headers += "Connection: close\r\n"
                headers += "\r\n"  # End of headers
                
                status_line = "HTTP/1.1 200 OK\r\n"
                response = status_line.encode('utf-8') + headers.encode('utf-8') + file_content

            else:  # File not found
                response = "HTTP/1.1 404 Not Found\r\n\r\n<h1>404 Not Found</h1>".encode('utf-8')
                logging.error(f"File not found: {file_path}")

            # Send the response
            client_socket.sendall(response)
            client_socket.close()
            

if __name__ == "__main__":
    server = SimpleHttpServer()
    server.start()
