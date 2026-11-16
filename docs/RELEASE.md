# Windows 배포 안내

1. `main`의 **Python CI**가 Linux·Windows에서 모두 통과했는지 확인합니다.
2. 새 버전 태그(예: `v0.2.0`)를 만들고 GitHub에 푸시하면 **Windows EXE** 워크플로가 시작됩니다.
3. 이 워크플로는 단위 테스트 후 PyInstaller로 `PaperAssistant.exe`를 빌드하고 SHA-256 파일을 함께 GitHub Releases에 게시합니다.
4. 실제 Windows 10/11에서 DOCX 불러오기·원고 분석·보고서 저장·복사·새 DOCX 초안 저장을 직접 점검합니다.

아직 Microsoft Authenticode 코드 서명을 사용하지 않으므로 Windows SmartScreen 경고가 나타날 수 있습니다. 무작정 경고를 우회하도록 안내하지 않으며, 공식 릴리스와 해시를 먼저 확인합니다.

Word VBA 모듈은 EXE에 포함되지 않습니다. `.bas` 파일은 Word의 VBA 편집기에서 **하나만** 수동으로 가져오며, 원본 문서 복사본에서 먼저 사용해 보세요.
