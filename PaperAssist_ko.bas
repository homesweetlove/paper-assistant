Attribute VB_Name = "PaperAssist"
Option Explicit

Public AssistOn As Boolean
Public LongSentLimit As Long

' 워드 시작 시 자동으로 실시간 검사 켜기
Sub AutoExec()
    검사켜기
End Sub

Sub 검사켜기()
    If LongSentLimit = 0 Then LongSentLimit = 100
    If AssistOn Then Exit Sub
    AssistOn = True
    LiveTick
End Sub

Sub 검사끄기()
    AssistOn = False
End Sub

' 1초마다 현재 문단 자동 검사
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

' 현재 문서 전체 검사 (Alt+F8로 실행)
Sub 전체검사()
    Dim p As Paragraph
    Application.ScreenUpdating = False
    For Each p In ActiveDocument.Paragraphs
        CheckParagraph p.Range
    Next
    Application.ScreenUpdating = True
    MsgBox "전체 검사 완료" & vbCrLf & _
           "노랑: 긴 문장 / 분홍: 구어체,1인칭,수식어 / 하늘: 감탄,의문문", vbInformation
End Sub

Sub 표시지우기()
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
    Static reEnd As Object
    If reEnd Is Nothing Then
        Set reEnd = CreateObject("VBScript.RegExp")
        reEnd.Pattern = "(해요|했어요|이에요|예요|이예요|죠|네요|거든요|잖아요|군요|구나|어라)\s*[.!?']?\s*$"
    End If
    If reEnd.Test(Trim(t)) Then HasStyleIssue = True: Exit Function

    Dim w As Variant
    For Each w In Array("내가 ", "저는 ", "우리는 ", "매우 ", "정말 ", "아주 ", "굉장히 ", "엄청 ", "되게 ", "진짜 ")
        If InStr(t, w) > 0 Then HasStyleIssue = True: Exit Function
    Next

    Dim opener As Variant
    For Each opener In Array("그래서", "근데", "그리고", "하지만", "그런데", "그러면")
        If Left$(Trim(t), Len(opener)) = opener Then HasStyleIssue = True: Exit Function
    Next
End Function
