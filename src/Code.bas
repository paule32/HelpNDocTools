Option Explicit

' ========= Einstellungen =========
Private Const TAB_HEIGHT_PT As Single = 40       ' Höhe des Bookmarks (vertikal)
Private Const TAB_OFFSET_TOP_PT As Single = 40   ' Abstand von oben
Private Const TAB_STEPS As Long = 0              ' 0 = keine Staffelung; >0 = Anzahl Stufen (z. B. 8)
Private Const TAB_STEP_PITCH_PT As Single = 55   ' Vertikalabstand je Stufe (wenn gestaffelt)

Private Const USE_PAGE_FIELD As Boolean = False  ' True = {PAGE}-Feld (nicht editierbar), False = Text (editierbar)

' ===== Optik / Geometrie =====
Private Const LINE_WEIGHT_PT As Single = 3       ' ~ 4 Pixel
Private Const FONT_NAME As String = "Arial Black"
Private Const FONT_SIZE As Single = 16

Private Const TEXT_COLOR As Long = vbBlack

Private Const BOX_FILL_R As Long = 240
Private Const BOX_FILL_G As Long = 240
Private Const BOX_FILL_B As Long = 240

Private Const BOX_LINE_COLOR As Long = vbBlack
Private Const BOX_LINE_PT As Single = 3

Private Const RULE_PT As Single = 2                 ' Liniendicke
Private Const RULE_R As Long = 80                   ' Linie dunkelgrau
Private Const RULE_G As Long = 80
Private Const RULE_B As Long = 80

' Farben (RGB)
Private Const COL_LINE_R As Long = 0
Private Const COL_LINE_G As Long = 0
Private Const COL_LINE_B As Long = 0

Private Const COL_FILL_R As Long = 0
Private Const COL_FILL_G As Long = 51
Private Const COL_FILL_B As Long = 200

Private Const COL_TEXT_R As Long = 255
Private Const COL_TEXT_G As Long = 255
Private Const COL_TEXT_B As Long = 0

' Tags zum Wiederfinden/Löschen
Private Const TAG_TEXTBOX As String = "HeaderLike_Text"
Private Const TAG_RULE As String = "HeaderLike_Rule"

Private Const BOX_HEIGHT_PT As Single = 32          ' Höhe der Kopf-Textbox
Private Const BOX_TOP_OFFSET_PT As Single = 6       ' Abstand unterhalb Top-Margin (optisch)
Private Const RULE_OFFSET_PT As Single = 2          ' Linie genau am unteren Rand der Kopfzone: TopMargin - 2pt

' 5 px ? pt (bei 96 dpi): 5 * 72 / 96 = 3.75 pt
Private Const CORNER_RADIUS_PT As Single = 3.75

' ---- Ersatz für Application.Min ----
Private Function MinSng(a As Single, b As Single) As Single
    If a < b Then MinSng = a Else MinSng = b
End Function

' ---- Ersatz für Application.Max ----
Private Function MaxSng(a As Single, b As Single) As Single
    If a > b Then
        MaxSng = a
    Else
        MaxSng = b
    End If
End Function

' ===== Hauptroutine =====
Public Sub InsertHeaderLikeFromTxt()
    Dim f As String
    f = PickTextFile()
    If Len(f) = 0 Then Exit Sub
    
    Dim lines() As String
    lines = ReadAllLines(f)
    If UBound(lines) < 0 Then
        MsgBox "Die Textdatei enthielt keine Zeilen.", vbExclamation
        Exit Sub
    End If
    
    Application.ScreenUpdating = False
    
    Dim doc As Document: Set doc = ActiveDocument
    Dim totalPages As Long: totalPages = doc.ComputeStatistics(wdStatisticPages)
    Dim p As Long, lineIdx As Long: lineIdx = 0
    
    ' Bestehende „Header-ähnliche“ Shapes entfernen (Neuaufbau)
    RemoveHeaderLikeShapes False
    
    For p = 1 To totalPages
        Dim r As Range, ps As PageSetup
        Set r = doc.GoTo(What:=wdGoToPage, Which:=wdGoToAbsolute, Count:=p)
        r.Collapse wdCollapseStart
        Set ps = r.Sections(1).PageSetup
        
        ' Geometrie
        Dim pageInnerLeft As Single, pageInnerWidth As Single
        pageInnerLeft = ps.LeftMargin
        pageInnerWidth = ps.PageWidth - ps.LeftMargin - ps.RightMargin
        
        ' ---- Linie über gesamte Seitenbreite ----
        AddFullWidthRule r, ps
        
        ' ---- Textbox über Satzspiegelbreite (links oder rechts ausgerichtet) ----
        Dim boxLeft As Single, boxTop As Single, boxWidth As Single
        boxLeft = pageInnerLeft
        boxTop = MaxSng(0, ps.TopMargin - BOX_HEIGHT_PT) + BOX_TOP_OFFSET_PT
        boxWidth = pageInnerWidth
        
        ' --- NEU (abgerundetes Rechteck) ---
        Dim shp As Shape
        Set shp = doc.Shapes.AddShape( _
            Type:=msoShapeRoundedRectangle, _
            Left:=boxLeft, Top:=boxTop, _
            Width:=boxWidth, Height:=BOX_HEIGHT_PT, _
            Anchor:=r)
            
        ' Rundung auf ca. 5 px einstellen
        shp.Adjustments(1) = CornerAdjustFor(boxWidth, BOX_HEIGHT_PT, CORNER_RADIUS_PT)
        
        StyleHeaderLikeBox shp
        
        ' Paritätsbündigkeit: ungerade links, gerade rechts
        If (p Mod 2 = 1) Then
            shp.TextFrame.TextRange.ParagraphFormat.Alignment = wdAlignParagraphLeft
        Else
            shp.TextFrame.TextRange.ParagraphFormat.Alignment = wdAlignParagraphRight
        End If
        
        ' Zeile der Datei setzen (falls weniger Zeilen als Seiten ? leer)
        Dim textLine As String
        If lineIdx <= UBound(lines) Then
            textLine = lines(lineIdx)
        Else
            textLine = ""
        End If
        lineIdx = lineIdx + 1
        
        ' Inhalt schreiben + **fett** / *kursiv* anwenden
        With shp.TextFrame.TextRange
            .Text = textLine
            .Font.Name = FONT_NAME
            .Font.Size = FONT_SIZE
            .Font.Bold = True
            .Font.Color = TEXT_COLOR
        End With
        ApplyMiniMarkup shp.TextFrame.TextRange   ' **bold**, *italic*
        
        shp.ZOrder msoBringToFront
    Next p
    
    Application.ScreenUpdating = True
    ' MsgBox "Fertig: " & (lineIdx) & " Zeile(n) auf " & totalPages & " Seite(n) verteilt." & vbCrLf & _
    '       "Ungerade Seiten: links · Gerade Seiten: rechts · Linie: 2pt dunkelgrau.", vbInformation
End Sub

' ===== Linie über ganze Seite (pro Seite) =====
Private Sub AddFullWidthRule(ByVal anchorRng As Range, ByVal ps As PageSetup)
    Dim y As Single
    y = MaxSng(0, ps.TopMargin - RULE_OFFSET_PT)
    Dim ln As Shape
    Set ln = anchorRng.Document.Shapes.AddLine(0, y, ps.PageWidth, y, anchorRng)
    With ln
        .AlternativeText = TAG_RULE
        .RelativeHorizontalPosition = wdRelativeHorizontalPositionPage
        .RelativeVerticalPosition = wdRelativeVerticalPositionPage
        .WrapFormat.Type = wdWrapNone
        .LockAnchor = True
        .Line.Weight = RULE_PT
        .Line.ForeColor.RGB = RGB(RULE_R, RULE_G, RULE_B)
        .LayoutInCell = False
        .ZOrder msoSendBehindText
    End With
End Sub

' ===== Box-Styling & Verhalten (schwebend, seitenbezogen) =====
Private Sub ForceVerticalCenter(ByVal shp As Shape)
    With shp
        ' (1) Klassischer TextFrame
        With .TextFrame
            .AutoSize = False                ' wichtig!
            .MarginTop = 0
            .MarginBottom = 0
            .VerticalAnchor = msoAnchorMiddle
            With .TextRange.ParagraphFormat
                .SpaceBefore = 0
                .SpaceAfter = 0
                .LineSpacingRule = wdLineSpaceSingle
                .Alignment = .Alignment      ' (nur liest/schreibt, belässt Links/Rechts)
            End With
        End With
        
        ' (2) Neuere TextFrame2-Eigenschaften (falls vorhanden)
        On Error Resume Next
        .TextFrame2.AutoSize = msoAutoSizeNone
        .TextFrame2.MarginTop = 0
        .TextFrame2.MarginBottom = 0
        .TextFrame2.VerticalAnchor = msoAnchorMiddle
        With .TextFrame2.TextRange.ParagraphFormat
            .SpaceBefore = 0
            .SpaceAfter = 0
            .FirstLineIndent = 0
        End With
        On Error GoTo 0
    End With
End Sub

Private Sub StyleHeaderLikeBox(ByVal shp As Shape)
    With shp
        .AlternativeText = TAG_TEXTBOX
        .RelativeHorizontalPosition = wdRelativeHorizontalPositionPage
        .RelativeVerticalPosition = wdRelativeVerticalPositionPage
        .WrapFormat.Type = wdWrapNone
        .LockAnchor = True
        .LayoutInCell = False
        
        ' Rahmen/Füllung
        .Line.Visible = msoTrue
        .Line.ForeColor.RGB = BOX_LINE_COLOR
        .Line.Weight = BOX_LINE_PT
        .Fill.Visible = msoTrue
        .Fill.Solid
        .Fill.ForeColor.RGB = RGB(BOX_FILL_R, BOX_FILL_G, BOX_FILL_B)
        .Fill.Transparency = 0
        
        With .TextFrame
            .MarginLeft = 4: .MarginRight = 4
            .MarginTop = 0: .MarginBottom = 0
            .VerticalAnchor = msoAnchorMiddle   ' << vertikal zentriert
            ' optional glatter Look:
            .AutoSize = False                   ' Höhe beibehalten
        End With
    End With
End Sub

' ===== Mini-Markup: **bold** und *italic* =====
Private Sub ApplyMiniMarkup(ByVal rng As Range)
    ' Reihenfolge: erst **fett**, dann *kursiv*
    ApplyDelimitedStyle rng, "**", True, False
    ApplyDelimitedStyle rng, "*", False, True
End Sub

Private Sub ApplyDelimitedStyle(ByVal base As Range, ByVal delim As String, _
                                ByVal makeBold As Boolean, ByVal makeItalic As Boolean)
    Dim s As Long, e As Long, txt As String
    Do
        txt = base.Text
        s = InStr(1, txt, delim, vbBinaryCompare)
        If s = 0 Then Exit Do
        e = InStr(s + Len(delim), txt, delim, vbBinaryCompare)
        If e = 0 Then Exit Do
        
        Dim inner As Range, openDel As Range, closeDel As Range
        Set inner = base.Duplicate
        inner.Start = base.Start + s - 1 + Len(delim)
        inner.End = base.Start + e - 1
        If makeBold Then inner.Font.Bold = True
        If makeItalic Then inner.Font.Italic = True
        
        Set closeDel = base.Duplicate
        closeDel.Start = base.Start + e - 1
        closeDel.End = closeDel.Start + Len(delim)
        closeDel.Text = ""
        
        Set openDel = base.Duplicate
        openDel.Start = base.Start + s - 1
        openDel.End = openDel.Start + Len(delim)
        openDel.Text = ""
    Loop
End Sub

' ===== Text-Datei wählen & einlesen =====
Private Function PickTextFile() As String
    With Application.FileDialog(msoFileDialogFilePicker)
        .Title = "Textdatei mit Überschriften-Zeilen wählen"
        .Filters.Clear
        .Filters.Add "Textdateien", "*.txt", 1
        .AllowMultiSelect = False
        If .Show = -1 Then
            PickTextFile = .SelectedItems(1)
        Else
            PickTextFile = ""
        End If
    End With
End Function

Private Function ReadAllLines(ByVal path As String) As String()
    Dim f As Integer: f = FreeFile
    Dim buf As String, arr() As String
    Open path For Input As #f
    buf = Input$(LOF(f), f)
    Close #f
    If Len(buf) = 0 Then
        ReDim arr(-1 To -1)
    Else
        arr = Split(Replace(buf, vbCrLf, vbLf), vbLf)
    End If
    ReadAllLines = arr
End Function

' ---------- Style auf eine Shape anwenden ----------
Private Sub ApplySideTabStyle(ByVal shp As Shape)
    With shp
        .WrapFormat.Type = wdWrapFront
        .LayoutInCell = False
        .RelativeHorizontalPosition = wdRelativeHorizontalPositionPage
        .RelativeVerticalPosition = wdRelativeVerticalPositionPage
        
        .Line.Visible = msoTrue
        .Line.ForeColor.RGB = RGB(COL_LINE_R, COL_LINE_G, COL_LINE_B)
        .Line.Weight = LINE_WEIGHT_PT
        
        .Fill.Visible = msoTrue
        .Fill.Solid
        .Fill.ForeColor.RGB = RGB(COL_FILL_R, COL_FILL_G, COL_FILL_B)
        .Fill.Transparency = 0
        
        With .TextFrame
            .MarginLeft = 2: .MarginRight = 2
            .MarginTop = 1: .MarginBottom = 1
            With .TextRange
                .ParagraphFormat.Alignment = wdAlignParagraphCenter
                .Font.Name = FONT_NAME
                .Font.Size = FONT_SIZE
                .Font.Bold = True
                .Font.Color = RGB(COL_TEXT_R, COL_TEXT_G, COL_TEXT_B)
            End With
        End With
    End With
End Sub

' ---------- Einfügen: ungerade rechts, gerade links ----------
Public Sub AddSideTabs_EvenLeft_OddRight()
    Dim doc As Document
    Dim pgCount As Long, p As Long
    Dim r As Range
    Dim shp As Shape
    Dim leftPos As Single, topPos As Single, widthPos As Single
    Dim ps As PageSetup
    Dim pageText As String
    Dim isOdd As Boolean
    
    Set doc = ActiveDocument
    DoEvents
    pgCount = doc.ComputeStatistics(wdStatisticPages)
    If pgCount < 1 Then Exit Sub
    
    Application.ScreenUpdating = False
    
    For p = 1 To pgCount
        ' An Seitenanfang der Seite p
        Set r = doc.GoTo(What:=wdGoToPage, Which:=wdGoToAbsolute, Count:=p)
        r.Collapse wdCollapseStart
        Set ps = r.Sections(1).PageSetup
        
        ' Staffelung / vertikale Position
        If TAB_STEPS > 0 Then
            topPos = ps.TopMargin + ((p - 1) Mod TAB_STEPS) * TAB_STEP_PITCH_PT
        Else
            topPos = ps.TopMargin + TAB_OFFSET_TOP_PT
        End If
        
        ' Seitenparität bestimmen
        isOdd = (p Mod 2 = 1)
        
        ' Ungerade = rechts, Gerade = links
        If isOdd Then
            ' Rechts: Start genau an rechter Satzkante, Breite bis Papierkante
            leftPos = ps.PageWidth - ps.RightMargin
            widthPos = ps.RightMargin
        Else
            ' Links: von Papierkante bis linke Satzkante
            leftPos = 0
            widthPos = ps.LeftMargin
        End If
        
        ' Inhalt: editierbar (oder Feld, wenn gewünscht)
        If USE_PAGE_FIELD Then
            pageText = ""
        Else
            pageText = CStr(p)
        End If
        
        ' Textbox hinzufügen
        Set shp = doc.Shapes.AddTextbox( _
            Orientation:=msoTextOrientationHorizontal, _
            Left:=leftPos, Top:=topPos, _
            Width:=widthPos, Height:=TAB_HEIGHT_PT, _
            Anchor:=r)
        
        shp.AlternativeText = "SideTab"
        ApplySideTabStyle shp
        
        If USE_PAGE_FIELD Then
            shp.TextFrame.TextRange.Fields.Add Range:=shp.TextFrame.TextRange, Type:=wdFieldPage
        Else
            shp.TextFrame.TextRange.Text = pageText
        End If
        
        shp.ZOrder msoBringToFront
    Next p
    
    Application.ScreenUpdating = True
    MsgBox "Bookmarks eingefügt: ungerade Seiten rechts, gerade Seiten links.", vbInformation
End Sub

' ---------- Vorhandene SideTabs nachträglich neu stylen ----------
Public Sub UpdateSideTabsStyles()
    Dim doc As Document, i As Long, n As Long
    Set doc = ActiveDocument
    Application.ScreenUpdating = False
    
    For i = 1 To doc.Shapes.Count
        If LCase$(doc.Shapes(i).AlternativeText) = "sidetab" Then
            ApplySideTabStyle doc.Shapes(i)
            doc.Shapes(i).ZOrder msoBringToFront
            n = n + 1
        End If
    Next i
    
    Application.ScreenUpdating = True
    MsgBox n & " SideTab(s) aktualisiert.", vbInformation
End Sub

' ===== Aufräumen =====
' --- Aufrufbare Wrapper-Prozedur für Alt+F8 ---
Public Sub RemoveHeaderLikeShapes_Run()
    RemoveHeaderLikeShapes False
End Sub

Public Sub RemoveHeaderLikeShapes(Optional ByUser As Boolean = True)
    Dim doc As Document: Set doc = ActiveDocument
    Dim i As Long, removed As Long
    Application.ScreenUpdating = False
    For i = doc.Shapes.Count To 1 Step -1
        With doc.Shapes(i)
            If LCase$(.AlternativeText) = LCase$(TAG_TEXTBOX) _
               Or LCase$(.AlternativeText) = LCase$(TAG_RULE) Then
                .Delete
                removed = removed + 1
            End If
        End With
    Next i
    Application.ScreenUpdating = True
    If ByUser Then MsgBox removed & " Header-ähnliche Shape(s) entfernt.", vbInformation
End Sub

' ---------- Entfernen ----------
Public Sub RemoveSideTabs()
    Dim doc As Document
    Dim i As Long, removed As Long
    
    Set doc = ActiveDocument
    Application.ScreenUpdating = False
    
    For i = doc.Shapes.Count To 1 Step -1
        If LCase$(doc.Shapes(i).AlternativeText) = "sidetab" Then
            doc.Shapes(i).Delete
            removed = removed + 1
        End If
    Next i
    
    Application.ScreenUpdating = True
    MsgBox removed & " Bookmark(s) entfernt.", vbInformation
End Sub


Public Sub Disable_SelectObjectsWithText()
    On Error Resume Next
    ' Manche Word-Versionen haben diese Option als Property:
    ' (Der Property-Name ist nicht in allen Builds gleich; deshalb defensiv.)
    Call ByNameSet(Application.Options, "IncludeShapesWithTextSelection", False)
    Call ByNameSet(Application.Options, "SelectObjectsWithText", False)
    On Error GoTo 0
    MsgBox "Falls vorhanden, wurde 'Objekte mit Textmarkierung auswählen' deaktiviert." & vbCrLf & _
           "Bitte ggf. zusätzlich manuell prüfen: Datei > Optionen > Erweitert.", vbInformation
End Sub

Private Sub ByNameSet(obj As Object, propName As String, val As Variant)
    ' Kleiner Helfer: setzt eine Option per Late Binding, falls vorhanden
    Dim v
    v = CallByName(obj, propName, VbGet)
    CallByName obj, propName, VbLet, val
End Sub

' Rechnet eine Ziel-Rundung in Punkten auf den Anpassungswert (0..0.5) um.
Private Function CornerAdjustFor(ByVal widthPt As Single, ByVal heightPt As Single, _
                                 ByVal radiusPt As Single) As Single
    ' Für msoShapeRoundedRectangle ist Adjustments(1) ~ Anteil (0..0.5) bezogen auf die kleinere Kante.
    Dim halfMin As Single: halfMin = MinSng(widthPt, heightPt) / 2!
    If halfMin <= 0 Then
        CornerAdjustFor = 0
    Else
        CornerAdjustFor = radiusPt / halfMin
        If CornerAdjustFor < 0 Then CornerAdjustFor = 0
        If CornerAdjustFor > 0.5 Then CornerAdjustFor = 0.5
    End If
End Function

