' Call generalized procedure for error handling and check result to
' decide where to resume
Private Sub CodeWithErrorHandler()
On Error GoTo ErrHandler
'...Procedure code ...
'...
Exit Sub

ErrHandler:
'Pass error to general purpose error-handling routine
Action = HandleError(Err.Number)
'Take action based on result of function
If Action = MyResume Then
  Resume ' execute same line of code
ElseIf Action = MyResumeNext Then
  Resume Next ' execute next line of code
End If
End Sub

Private Function HandleError(ErrNum As Integer) As Integer
Select Case Err.Num
  Case 53 'File not found
    answer=MsgBox("File not found. Try again?", _
    vbYesNo)

  Case 76 'Path not found
    answer=MsgBox("Path not found. Try again?", _
    vbYesNo)

  Case Else 'unknown error
    MsgBox "Unknown error. Quitting now." 'SHOULD LOG ERROR!
    Unload Me
End Select

If answer = vbYes Then
  HandleError = MyResume 'tell calling procedure to resume
ElseIf answer = vbNo Then
  HandleError = MyResumeNext 'tell calling procedure to resume next
End If

End Function