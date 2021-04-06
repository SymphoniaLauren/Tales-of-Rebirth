using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;

namespace fpb
{
    class Program
        // This program repacks DAT.BIN for Tales of Rebirth (PS2)
    {
        static readonly uint pointerBegin = 0xD76B0;
        static void Main(string[] args)
        {
            string text = File.ReadAllText("dat.json");
            Dictionary<string, string> jsonData = JsonSerializer.Deserialize<Dictionary<string, string>>(text);
            List<uint> sectors = new List<uint>() { 0 };
            List<uint> remainders = new List<uint>();
            uint buffer = 0;
            BinaryWriter output = new BinaryWriter(File.Open("DAT_NEW2.dat", FileMode.OpenOrCreate, FileAccess.Write));
            foreach (KeyValuePair<string, string> pair in jsonData)
            {
                uint size = 0;
                uint remainder = 0;
                if (pair.Value != "dummy")
                {
                    string fileName = String.Format("dat/{0}.{1}", pair.Key, pair.Value);
                    if (!File.Exists(fileName))
                    {
                        continue;
                    }
                    BinaryReader file = new BinaryReader(File.Open(fileName, FileMode.Open, FileAccess.Read));
                    size = (uint)file.BaseStream.Length;
                    output.Write(file.ReadBytes((int)size));
                    remainder = 0x40 - (size % 0x40);
                    remainder = remainder == 0x40 ? 0 : remainder;
                    for (int i = 0; i < remainder; i++)
                    {
                        output.Write((byte)0);
                    }
                    file.Close();
                }
                remainders.Add(remainder);
                buffer += size + remainder;
                sectors.Add(buffer);
                Console.WriteLine("{0}.{1}", pair.Key, pair.Value);
            }
            output.Close();
            BinaryWriter slps = new BinaryWriter(File.Open("NEW_SLPS_254.50", FileMode.Open, FileAccess.Write));
            slps.BaseStream.Position = pointerBegin;
            for (int i = 0; i < sectors.Count - 1; i++)
            {
                slps.Write(sectors[i] + remainders[i]);
            }
            slps.Close();
        }
    }
}
