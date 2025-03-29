using System;
using System.Threading.Tasks;
using Microsoft.AspNetCore.SignalR.Client;
using System.IO;

class Program
{
    static async Task Main(string[] args)
    {
        Console.WriteLine("Starting simple JSON sender application...");
        
        try
        {
            // 1. Find and read message_data.json
            string jsonFilePath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "message_data.json");
            
            if (!File.Exists(jsonFilePath))
            {
                Console.WriteLine($"Error: File not found at {jsonFilePath}");
                Console.WriteLine("Press any key to exit...");
                Console.ReadKey();
                return;
            }
            
            // Read the JSON content
            string jsonMessage = File.ReadAllText(jsonFilePath);
            Console.WriteLine("Successfully loaded message_data.json");
            
            // 2. Connect to the SignalR hub
            string url = "https://backendhackathon202520250328210710.azurewebsites.net/hubs/gemini";
            var connection = new HubConnectionBuilder()
                .WithUrl(url)
                .WithAutomaticReconnect()
                .Build();
                
            Console.WriteLine("Connecting to SignalR hub...");
            await connection.StartAsync();
            Console.WriteLine("Successfully connected to the hub");
            
            // 3. Send the JSON message using ProcessPersonalizedQuestions with a single parameter
            Console.WriteLine("Sending JSON message using ProcessPersonalizedQuestions...");
            await connection.InvokeAsync("ProcessPersonalizedQuestions", jsonMessage);
            
            Console.WriteLine("Message sent successfully!");
            Console.WriteLine("JSON content (truncated):");
            if (jsonMessage.Length > 500)
                Console.WriteLine(jsonMessage.Substring(0, 500) + "...");
            else
                Console.WriteLine(jsonMessage);
            
            // 4. Close the connection
            await connection.StopAsync();
            Console.WriteLine("Connection closed");
            
            // 5. Wait for user input before exiting - with auto-exit support for automation
            Console.WriteLine("\nPress any key to exit...");
            
            bool fromPython = args.Length > 0 && args[0] == "--from-python";
            if (fromPython)
            {
                Console.WriteLine("Running from Python script - auto-exiting in 2 seconds...");
                await Task.Delay(2000);
                return;
            }
            
            Console.ReadKey();
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
            Console.WriteLine($"Stack trace: {ex.StackTrace}");
            Console.WriteLine("\nPress any key to exit...");
            Console.ReadKey();
        }
    }
}
