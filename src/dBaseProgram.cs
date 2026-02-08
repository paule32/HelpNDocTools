// ----------------------------------------------------------------------------
// \file  dBaseProgram.cs
// \note  (c) 2025, 2026 by Jens Kallup - paule32
//        all rights reserved.
// ----------------------------------------------------------------------------
using System;
using DBaseRuntime;

// Wichtig: passe Namespace/Klassennamen an dein generiertes File an!
public static class dBaseProgram
{
    public static void Main()
    {
        // Beispiel: wenn dein Generator "public class GenProg : ParentForm" erzeugt:
        var app = new GenProg();

        // Falls du Init() generierst oder erwartest:
        app.Init();

        // Beispiel: eine Methode aufrufen, die du generiert hast:
        // app.Test(null);

        Console.WriteLine("Done.");
    }
}
