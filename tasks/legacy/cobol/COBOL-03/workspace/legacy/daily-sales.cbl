       IDENTIFICATION DIVISION.
       PROGRAM-ID. DAILY-SALES.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT SALES-FILE ASSIGN TO "sales.dat"
              ORGANIZATION IS LINE SEQUENTIAL.
       DATA DIVISION.
       FILE SECTION.
       FD  SALES-FILE.
       01  SALES-RECORD.
           05 SALE-ID       PIC X(8).
           05 SALE-AMOUNT   PIC S9(7)V99 COMP-3.
           05 SALE-STATUS   PIC X.
       WORKING-STORAGE SECTION.
       01  WS-TOTAL        PIC S9(9)V99 COMP-3 VALUE 0.
       01  WS-END          PIC X VALUE "N".
       PROCEDURE DIVISION.
           OPEN INPUT SALES-FILE
           PERFORM UNTIL WS-END = "Y"
              READ SALES-FILE
                 AT END MOVE "Y" TO WS-END
                 NOT AT END
                    IF SALE-STATUS = "P"
                       ADD SALE-AMOUNT TO WS-TOTAL
                    END-IF
              END-READ
           END-PERFORM
           CLOSE SALES-FILE
           GOBACK.
