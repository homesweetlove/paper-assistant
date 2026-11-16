Attribute VB_Name = "PaperAssist"
Option Explicit

' 이 모듈 또는 PaperAssist.bas 중 하나만 가져오세요.
' 문서 시작 자동 실행과 반복 타이머는 사용하지 않습니다.
' 문서 본문과 기존 형광펜을 건드리지 않고 전용 댓글만 추가합니다.
Private Const COMMENT_PREFIX As String = "[PaperAssistant] "
Private Const MAX_COMMENTS As Long = 200
Public LongSentLimit As Long

Public Sub 전체검사()
    Dim para As Paragraph
    Dim s As Range
    Dim note As String
    Dim written As Long
    If Application.Documents.Count = 0 Then Exit Sub
    If LongSentLimit < 20 Then LongSentLimit = 100
    표시지우기
    On Error GoTo ReviewFailed
    For Each para In ActiveDocument.Paragraphs
        For Each s In para.Range.Sentences
            note = 검사설명(s.Text)
            If Len(note) > 0 Then
                ActiveDocument.Comments.Add Range:=s, Text:=COMMENT_PREFIX & note
                written = written + 1
                If written >= MAX_COMMENTS Then Exit For
            End If
        Next s
        If written >= MAX_COMMENTS Then Exit For
    Next para
    MsgBox "검토 댓글 " & written & "개를 추가했습니다." & vbCrLf & _
           "규칙 기반 참고 정보이며 오류를 확정하지 않습니다.", vbInformation
    Exit Sub
ReviewFailed:
    MsgBox "검사가 중단되었습니다: " & Err.Description, vbExclamation
End Sub

Public Sub 표시지우기()
    ' 도구가 만든 댓글만 지웁니다. 사용자가 넣은 댓글·형광펜은 보존합니다.
    Dim i As Long
    Dim c As Comment
    If Application.Documents.Count = 0 Then Exit Sub
    For i = ActiveDocument.Comments.Count To 1 Step -1
        Set c = ActiveDocument.Comments(i)
        If Left$(c.Range.Text, Len(COMMENT_PREFIX)) = COMMENT_PREFIX Then c.Delete
    Next i
End Sub

Private Function 검사설명(ByVal text As String) As String
    Dim current As String
    Dim w As Variant
    current = Trim$(Replace(Replace(text, vbCr, ""), vbLf, ""))
    If Len(current) < 2 Then Exit Function
    If Len(current) >= LongSentLimit Then
        검사설명 = "긴 문장입니다. 나눌 수 있는지 검토하세요."
        Exit Function
    End If
    If InStr(current, "!") > 0 Or InStr(current, "?") > 0 Then
        검사설명 = "감탄·의문 표현의 학술 문체 적합성을 확인하세요."
        Exit Function
    End If
    For Each w In Array("해요", "했어요", "이에요", "예요", "거든요", "잖아요")
        If Right$(current, Len(w)) = w Or Right$(current, Len(w) + 1) = w & "." Then
            검사설명 = "구어체 종결 표현을 검토하세요."
            Exit Function
        End If
    Next w
    For Each w In Array("내가 ", "저는 ", "우리는 ", "매우 ", "정말 ", "굉장히 ", "진짜 ")
        If InStr(current, w) > 0 Then
            검사설명 = "1인칭 또는 주관적 수식어가 있는지 확인하세요."
            Exit Function
        End If
    Next w
End Function
