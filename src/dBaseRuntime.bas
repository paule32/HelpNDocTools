' ----------------------------------------------------------------------------
' \file  dBaseRuntime.bas
' \note  (c) 2025, 2026 by Jens Kallup - paule32
'        all rights reserved.
' ----------------------------------------------------------------------------
Option Compare Database
Option Explicit

' ----------------------------------------------------------------------------
' dBase-ish helpers
' ----------------------------------------------------------------------------
Public Sub WRITE(ParamArray args() As Variant)
    Dim i As Long
    If (UBound(args) - LBound(args) + 1) <= 0 Then
        Debug.Print
        Exit Sub
    End If
    For i = LBound(args) To UBound(args)
        Debug.Print args(i)
    Next i
End Sub

' ----------------------------------------------------------------------------
' Factory: NEW "PushButton", "Ok"
' ----------------------------------------------------------------------------
Public Function NEWOBJ(ByVal className As String, ParamArray args() As Variant) As Object
    Dim cn As String
    cn = UCase$(className)

    Select Case cn
        Case "PUSHBUTTON"
            Dim b As PushButton
            Set b = New PushButton
            If (UBound(args) - LBound(args) + 1) > 0 Then
                b.Init CStr(args(LBound(args)))
            End If
            Set NEWOBJ = b

        ' TODO: weitere Klassen hier ergänzen
        Case Else
            Err.Raise vbObjectError + 513, "RT.NEWOBJ", "Unbekannte Klasse: " & className
    End Select
End Function
