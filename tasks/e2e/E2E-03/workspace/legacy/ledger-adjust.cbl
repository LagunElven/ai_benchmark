       IDENTIFICATION DIVISION.
       PROGRAM-ID. LEDGER-ADJUST.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-BALANCE  PIC S9(9)V99 COMP-3.
       01 WS-AMOUNT   PIC  9(9)V99 COMP-3.
       01 WS-TYPE     PIC X.
       01 WS-ERROR    PIC X VALUE "N".
       PROCEDURE DIVISION.
           EVALUATE WS-TYPE
              WHEN "C"
                 ADD WS-AMOUNT TO WS-BALANCE
              WHEN "D"
                 SUBTRACT WS-AMOUNT FROM WS-BALANCE
              WHEN "N"
                 CONTINUE
              WHEN OTHER
                 MOVE "Y" TO WS-ERROR
           END-EVALUATE
           GOBACK.
