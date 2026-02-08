// ----------------------------------------------------------------------------
// \file  dBaseRuntime.cs
// \note  (c) 2025, 2026 by Jens Kallup - paule32
//        all rights reserved.
// ----------------------------------------------------------------------------
using System;
using System.Collections.Generic;

namespace DBaseRuntime
{
    // dBase-like helper API
    public static class RT
    {
        // WRITE-Äquivalent (falls du es nicht direkt als Console.WriteLine generierst)
        public static void WRITE(object? x) => Console.WriteLine(x);

        // dBase NIL
        public static object? NIL => null;

        // dBase IIF(cond, a, b)
        public static object? IIF(bool cond, object? a, object? b) => cond ? a : b;

        // dBase VAL("123") etc.
        public static double VAL(object? s)
        {
            if (s == null) return 0;
            if (s is double d) return d;
            if (s is int i) return i;
            double.TryParse(s.ToString(), out var r);
            return r;
        }

        // dBase STR(123)
        public static string STR(object? x) => x?.ToString() ?? "";

        // einfache Vergleichshilfe, falls du später "Variant"-Vergleiche brauchst
        public static bool EQ(object? a, object? b) => Equals(a, b);
    }

    // Ein sehr einfacher Basistyp für deine Forms (kann später wachsen)
    public class ParentForm
    {
        // Platzhalter für gemeinsame Properties
        public object? THIS => this;

        public virtual void Init()
        {
            // optional
        }
    }

    // Minimaler UI-Platzhalter (damit new PushButton("Ok") + .Text kompiliert)
    public class PushButton
    {
        public string Text   { get; set; } = "";
        public double Left   { get; set; }
        public double Top    { get; set; }
        public double Width  { get; set; }
        public double Height { get; set; }

        public PushButton() { }
        public PushButton(string text) { Text = text; }

        public override string ToString() => $"PushButton(Text='{Text}')";
    }
}
