       IDENTIFICATION DIVISION.
       PROGRAM-ID. ACCOUNT-STATUS.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-BALANCE        PIC S9(7)V99 COMP-3.
       01 WS-DAYS-PAST-DUE  PIC 9(3).
       01 WS-STATUS         PIC X.
       PROCEDURE DIVISION.
           IF WS-BALANCE = 0
              MOVE "Z" TO WS-STATUS
           ELSE
              IF WS-DAYS-PAST-DUE > 30
                 MOVE "D" TO WS-STATUS
              ELSE
                 MOVE "A" TO WS-STATUS
              END-IF
           END-IF
           GOBACK.
