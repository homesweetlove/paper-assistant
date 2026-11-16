Attribute VB_Name = "PaperAssist"
Option Explicit

' Import ONE module: PaperAssist.bas OR PaperAssist_ko.bas, never both.
' No AutoExec or repeating OnTime timer: review only runs on explicit request.
' The tool adds labeled comments, never changes document highlights or text.
Private Const COMMENT_PREFIX As String = "[PaperAssistant] "
Private Const MAX_COMMENTS As Long = 200
Public LongSentLimit As Long

Public Sub CheckAll()
    Dim para As Paragraph
    Dim sentence As Range
    Dim note As String
    Dim written As Long
    If Application.Documents.Count = 0 Then Exit Sub
    If LongSentLimit < 20 Then LongSentLimit = 100
    ClearMarks
    On Error GoTo ReviewFailed
    For Each para In ActiveDocument.Paragraphs
        For Each sentence In para.Range.Sentences
            note = SuggestionFor(sentence.Text)
            If Len(note) > 0 Then
                ActiveDocument.Comments.Add Range:=sentence, Text:=COMMENT_PREFIX & note
                written = written + 1
                If written >= MAX_COMMENTS Then Exit For
            End If
        Next sentence
        If written >= MAX_COMMENTS Then Exit For
    Next para
    MsgBox "Review comments added: " & written & vbCrLf & _
           "This is a rule-based suggestion, not a correctness verdict.", vbInformation
    Exit Sub
ReviewFailed:
    MsgBox "Review stopped: " & Err.Description, vbExclamation
End Sub

Public Sub ClearMarks()
    ' Keep every pre-existing highlight and every user-authored comment.
    Dim i As Long
    Dim c As Comment
    If Application.Documents.Count = 0 Then Exit Sub
    For i = ActiveDocument.Comments.Count To 1 Step -1
        Set c = ActiveDocument.Comments(i)
        If Left$(c.Range.Text, Len(COMMENT_PREFIX)) = COMMENT_PREFIX Then c.Delete
    Next i
End Sub

Private Function SuggestionFor(ByVal text As String) As String
    Dim current As String
    current = Trim$(Replace(Replace(text, vbCr, ""), vbLf, ""))
    If Len(current) < 2 Then Exit Function
    If Len(current) >= LongSentLimit Then
        SuggestionFor = "Long sentence; consider splitting it."
    ElseIf InStr(current, "!") > 0 Or InStr(current, "?") > 0 Then
        SuggestionFor = "Question or exclamation; review the academic tone."
    End If
End Function
