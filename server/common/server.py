from signal import signal
import socket
import logging
import multiprocessing


class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.listen_backlog = listen_backlog
        self.processes = []
        self.client_sockets = {}

    def run(self):

        signal.signal(signal.SIGTERM, self.exit_gracefully)

        processes_number = self.listen_backlog if self.listen_backlog <= multiprocessing.cpu_count(
        ) else multiprocessing.multiprocessing.cpu_count()
        for i in range(0, processes_number):
            p = multiprocessing.Process(
                target=self.__new_connection, args=(i,))
            p.start()
            self.processes.append(p)

    def __new_connection(self, client_id):
        """
        Dummy Process Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communication
        finishes, this process starts to accept new connections again
        """
        while True:
            client_sock = self.__accept_new_connection()
            self.client_sockets[client_id] = client_sock
            self.__handle_client_connection(client_sock, client_id)

    def __handle_client_connection(self, client_sock, client_id):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            msg = client_sock.recv(1024).rstrip().decode('utf-8')
            logging.info(
                'Message received from connection {}. Msg: {}'
                .format(client_sock.getpeername(), msg))
            client_sock.send(
                "Your Message has been received: {}\n".format(msg).encode('utf-8'))
        except OSError:
            logging.info("Error while reading socket {}".format(client_sock))
        finally:
            client_sock.close()
            del self.client_sockets[client_id]

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info("Proceed to accept new connections")
        c, addr = self._server_socket.accept()
        logging.info('Got connection from {}'.format(addr))
        return c

    def exit_gracefully(self, sig, frame):
        return
