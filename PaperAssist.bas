Attribute VB_Name = "PaperAssist"
Option Explicit

Public AssistOn As Boolean
Public LongSentLimit As Long

' Runs automatically when Word starts
Sub AutoExec()
    EnableAssist
End Sub

Sub EnableAssist()
    If LongSentLimit = 0 Then LongSentLimit = 100
    If AssistOn Then Exit Sub
    AssistOn = True
    LiveTick
End Sub

Sub DisableAssist()
    AssistOn = False
End Sub

' Checks the current paragraph every second
Sub LiveTick()
    On Error Resume Next
    If AssistOn Then
        If Application.Documents.Count > 0 Then
            CheckParagraph Application.Selection.Range.Paragraphs(1).Range
        End If
        Application.OnTime Now + TimeValue("0:00:01"), "LiveTick"
    End If
    On Error GoTo 0
End Sub

' Checks the whole document (run via Alt+F8)
Sub CheckAll()
    Dim p As Paragraph
    Application.ScreenUpdating = False
    For Each p In ActiveDocument.Paragraphs
        CheckParagraph p.Range
    Next
    Application.ScreenUpdating = True
    MsgBox "Done." & vbCrLf & _
           "Yellow = long sentence / Pink = colloquial style / Blue = question or exclamation", vbInformation
End Sub

Sub ClearMarks()
    ActiveDocument.Range.HighlightColorIndex = wdNoHighlight
End Sub

Sub CheckParagraph(rng As Range)
    Dim s As Range
    On Error Resume Next
    For Each s In rng.Sentences
        CheckSentence s
    Next
    On Error GoTo 0
End Sub

Sub CheckSentence(s As Range)
    Dim t As String
    t = s.Text
    If Len(Trim(t)) < 2 Then Exit Sub

    s.HighlightColorIndex = wdNoHighlight
    If Len(t) > LongSentLimit Then
        s.HighlightColorIndex = wdYellow
    ElseIf InStr(t, "!") > 0 Or InStr(t, "?") > 0 Then
        s.HighlightColorIndex = wdTurquoise
    ElseIf HasStyleIssue(t) Then
        s.HighlightColorIndex = wdPink
    End If
End Sub

Function HasStyleIssue(t As String) As Boolean
    ' Korean patterns are written as \uXXXX escapes to avoid encoding problems
    Static reEnd As Object, reWord As Object, reOpen As Object
    If reEnd Is Nothing Then
        Set reEnd = CreateObject("VBScript.RegExp")
        ' Colloquial endings: 해요 했어요 이에요 예요 이예요 죠 네요 거든요 잖아요 군요 구나 어라
        reEnd.Pattern = "(\ud574\uc694|\ud588\uc5b4\uc694|\uc774\uc5d0\uc694|\uc608\uc694|\uc774\uc608\uc694|\uc8e0|\ub124\uc694|\uac70\ub4e0\uc694|\uc796\uc544\uc694|\uad70\uc694|\uad6c\ub098|\uc5b4\ub77c)\s*[.!?'""]?\s*$"
        ' Bad words: 내가 저는 우리는 매우 정말 아주 굉장히 엄청 되게 진짜
        Set reWord = CreateObject("VBScript.RegExp")
        reWord.Pattern = "(\ub0b4\uac00|\uc800\ub294|\uc6b0\ub9ac\ub294|\ub9e4\uc6b0|\uc815\ub9d0|\uc544\uc8fc|\uad49\uc7a5\ud788|\uc5c4\uccad|\ub418\uac8c|\uc9c4\uc9dc)"
        ' Sentence openers: 그래서 근데 그리고 하지만 그런데 그러면
        Set reOpen = CreateObject("VBScript.RegExp")
        reOpen.Pattern = "^\s*(\uadf8\ub798\uc11c|\uadfc\ub370|\uadf8\ub9ac\uace0|\ud558\uc9c0\ub9cc|\uadf8\ub7f0\ub370|\uadf8\ub7ec\uba74)"
    End If
    HasStyleIssue = reEnd.Test(t) Or reWord.Test(t) Or reOpen.Test(t)
End Function
