Option Compare Database
Option Explicit

Public width As Variant
Public top As Variant

Public Function Init(ByVal a As Variant, ByVal c As Variant) As Variant
    Debug.Print
    Debug.Print
    Debug.Print
    Debug.Print
    I = 1
    E = 42
    Dim I As Long
    For I = 0 To 0 Step 1
            Debug.Print
            E = E+1
            Debug.Print
            Debug.Print
            Debug.Print
            If I==3 Then
                Exit Function
    End If
            Exit For
    Next
    Debug.Print
    Init = Null
End Function

Public Function TestProc(ByVal Sender As Variant) As Variant
    Debug.Print
    TestProc = 324
    Exit Function
    TestProc = Null
End Function

Public Function ParentForm_onClick(ByVal Sender As Variant) As Variant
    Debug.Print
    x = 5
    Debug.Print
    ' TODO stmt: StatementContext
    Debug.Print
    ' TODO stmt: StatementContext
    ParentForm_onClick = Null
End Function

Public Function PushButton1_onClick_1(ByVal Sender As Variant) As Variant
    Debug.Print
    Debug.Print
    ' TODO stmt: StatementContext
    If THIS.PushButton1.Text=="Click Me" Then
            THIS.PushButton2.Text = "Click Me"
            Debug.Print
            ' TODO stmt: StatementContext
    Else
            THIS.PushButton2.Text = "Click Me, too"
            Sender.Text = "Click Me"
            Sender.Font.bold = .F.
            Sender.Font.Size = 11
    End If
    PushButton1_onClick_1 = Null
End Function

Public Function PushButton1_onClick_2(ByVal Sender As Variant) As Variant
    Debug.Print
    PushButton1_onClick_2 = Null
End Function

Public Function PushButton1_onClick_3(ByVal Sender As Variant) As Variant
    Debug.Print
    PushButton1_onClick_3 = Null
End Function

Public Function PushButton1_onMouseRButton(ByVal Sender As Variant) As Variant
    Debug.Print
    PushButton1_onMouseRButton = Null
End Function

Public Function PushButton1_onMouseMove(ByVal Sender As Variant) As Variant
    Debug.Print
    PushButton1_onMouseMove = Null
End Function

Public Function PushButton2_onClick(ByVal Sender As Variant) As Variant
    Debug.Print
    Debug.Print
    If THIS.PushButton2.Text=="Click Me, too" Then
            THIS.PushButton1.Text = "Click Me"
            Sender.Text = "Click Me"
    Else
            THIS.PushButton1.Text = "Click Me"
            Sender.Text = "Click Me, too"
    End If
    PushButton2_onClick = Null
End Function