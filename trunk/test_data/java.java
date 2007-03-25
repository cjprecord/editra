// This example is from the book _Java in a Nutshell_ by David Flanagan.
// Written by David Flanagan.  Copyright (c) 1996 O'Reilly & Associates.
// You may study, use, modify, and distribute this example for any purpose.
// This example is provided WITHOUT WARRANTY either expressed or implied.

import java.io.*;
import java.net.*;

public class Client {
    public static final int DEFAULT_PORT = 6789;
    Socket socket;
    Thread reader, writer;

    // Create the client by creating its reader and writer threads
    // and starting them.
    public Client(String host, int port) {
        try { 
            socket = new Socket(host, port);
            // Create reader and writer sockets
            reader = new Reader(this);
            writer = new Writer(this);
            // Give the reader a higher priority to work around
            // a problem with shared access to the console.
            reader.setPriority(6);
            writer.setPriority(5);
            // Start the threads 
            reader.start();
            writer.start();
        }
        catch (IOException e) { System.err.println(e); }
    }

    public static void usage() {
        System.out.println("Usage: java Client <hostname> [<port>]");
        System.exit(0);
    }    
    public static void main(String[] args) {
        int port = DEFAULT_PORT;
        Socket s = null;
        
        // Parse the port specification
        if ((args.length != 1) && (args.length != 2)) usage();
        if (args.length == 1) port = DEFAULT_PORT;
        else {
            try { port = Integer.parseInt(args[1]); }
            catch (NumberFormatException e) { usage(); }
        }
        
        new Client(args[0], port);
    }
}

// This thread reads data from the server and prints it on the console
// As usual, the run() method does the interesting stuff.
class Reader extends Thread {
    Client client;
    public Reader(Client c) {
        super("Client Reader");
        this.client = c;
    }
    public void run() {
        DataInputStream in = null;
        String line;
        try {
            in = new DataInputStream(client.socket.getInputStream());
            while(true) {
                line = in.readLine();
                if (line == null) { 
                    System.out.println("Server closed connection.");
                    break;
                }
                System.out.println(line);
            }
        }
        catch (IOException e) { System.out.println("Reader: " + e); }
        finally { try {if (in != null) in.close();} catch (IOException e) {;} }
        System.exit(0);
    }
}

// This thread reads user input from the console and sends it to the server.
class Writer extends Thread {
    Client client;
    public Writer(Client c) {
        super("Client Writer");
        client = c;
    }
    public void run() {
        DataInputStream in = null;
        PrintStream out = null;
        try {
            String line;
            in = new DataInputStream(System.in);
            out = new PrintStream(client.socket.getOutputStream());
            while(true) {
                line = in.readLine();
                if (line == null) break;
                out.println(line);
            }
        }
        catch (IOException e) { System.err.println("Writer: " + e); }
        finally { if (out != null) out.close(); }
        System.exit(0);
    }
}
