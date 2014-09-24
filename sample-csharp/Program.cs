using System;
using System.Net;
using System.Threading;
using System.Linq;
using System.Text;
 
class Program {
    static void Main(string[] args) {
        SimpleWebServer.WebServer ws = new SimpleWebServer.WebServer(SendResponse, "http://localhost:8080/test/");
        ws.Run();
        Console.WriteLine("A simple webserver. Press a key to quit.");
        Console.ReadKey();
        ws.Stop();
    }
     
    public static string SendResponse(HttpListenerRequest request) {
        return string.Format("<HTML><BODY>My web page.<br>{0}</BODY></HTML>", DateTime.Now);    
    }
}
