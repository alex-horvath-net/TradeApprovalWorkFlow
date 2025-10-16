
## Trade Approval Workflow

> **Authorization Legend:**  
> R = Requester. Anyone can do it.<br>
> NR = Non-requester. Anyone except requester can do it.<br>
> A = Approver. Requester if NeedsReapproval was involved, otherwise None-requester<br>
> R/A = both Requester and Approver can do it, but noone else<br>


```mermaid

stateDiagram-v2
    direction TB

  

    [*] --> Draft : Create (R)
  

    %% Draft stage
    Draft --> Draft : Update (R)
    Draft --> PendingApproval: Submit (R) 
    Draft --> Cancelled: Cancel (R)
    
    %% Approval stages
    NeedsReapproval --> Approved: Approve (R)
    PendingApproval --> Approved: Approve (NR)
    PendingApproval --> NeedsReapproval: Update (NR)
    PendingApproval --> Cancelled: Cancel  (NR)
    
   
    NeedsReapproval --> Cancelled: Cancel (R) 
    
    Approved --> SentToCounterparty: SendToExecute (A)
    Approved --> Cancelled: Cancel (A)

    %% Post-approval
    SentToCounterparty --> Executed: Book (R/A)
    SentToCounterparty --> Cancelled: Cancel (R/A)    
    
    Cancelled --> [*]
    Executed --> [*]


```

## Layer diagram 
```mermaid
graph TD
    direction TB

    
    A[Test Layer] --> B
    
    B[Application Layer<br>
    -approval_service.py
    -commands<br>
    -interfaces<br>] --> D

    B-->E

    D[Domain Layer<br>
    -Models<br>
    -Exceptions<br>] 

    E[Infrastructure Layer<br>
    -Repository<br>
    -Executor<br>
    -Time] 

   
```

| **State**                  | **Action**        | **Transition**                    | **Input**                                   | **Assumptions**                                                                                                                                                              |
| -------------------------- | ----------------- | --------------------------------- | ------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| *(Trade not exists yet)* | **Create**        | → Draft                           | Requester UserId + TradeDetails             | 1️⃣ Requester can be anyone (no dedicated role).<br>2️⃣ TradeDetails must be validated.<br>3️⃣ Trade saved to database as the first version.                                 |
| **Draft**                  | **Submit**        | Draft → PendingApproval           | Requester UserId + TradeDetails             | 1️⃣ Only the Requester can submit their own draft.<br>2️⃣ No re-validation needed.<br>3️⃣ Trade saved to database as a new version.                                          |
| **Draft**                  | **Update**        | Draft → Draft                     | Requester UserId + TradeDetails             | 1️⃣ Only the Requester can update their own draft.<br>2️⃣ Cannot update after submission.<br>3️⃣ TradeDetails must be re-validated.<br>4️⃣ Trade saved as new version.       |
| **Draft**                  | **Cancel**        | Draft → Cancelled                 | Requester UserId                            | 1️⃣ Only the Requester can cancel their own draft.                                                                                                                           |
| **PendingApproval**        | **Approve**       | PendingApproval → Approved        | Approver UserId                             | 1️⃣ Approver = anyone except Requester.<br>2️⃣ No re-validation.<br>3️⃣ Trade saved as new version.                                                                          |
| **PendingApproval**        | **Update**        | PendingApproval → NeedsReapproval | Approver UserId + TradeDetails              | 1️⃣ Approver (not Requester) can update.<br>2️⃣ TradeDetails must be re-validated.<br>3️⃣ Trade saved as new version.                                                        |
| **PendingApproval**        | **Cancel**        | PendingApproval → Cancelled       | Approver UserId                             | 1️⃣ Approver (not Requester) can cancel.<br>2️⃣ Requester can cancel only drafts, not pending trades.<br>3️⃣ Trade saved as new version.                                     |
| **NeedsReapproval**        | **Approve**       | NeedsReapproval → Approved        | Requester UserId                            | 1️⃣ Original Requester approves the Approver’s change.<br>2️⃣ No re-validation.<br>3️⃣ Trade saved as new version.                                                           |
| **NeedsReapproval**        | **Cancel**        | NeedsReapproval → Cancelled       | Requester UserId                            | 1️⃣ Approver (not Requester) can cancel.<br>2️⃣ Requester can cancel only drafts, not pending trades.<br>3️⃣ Trade saved as new version.                                     |
| **Approved**               | **SendToExecute** | Approved → SentToCounterparty     | Actual Approver UserId                      | 1️⃣ Actual Approver = Approver of PendingApproval or NeedsReapproval (Requester).<br>2️⃣ Only Approver can send.<br>3️⃣ No re-validation.<br>4️⃣ Trade saved as new version. |
| **Approved**               | **Cancel**        | Approved → Cancelled              | Requester UserId                            | 1️⃣ Approver (not Requester) can cancel.<br>2️⃣ Requester can cancel only drafts.<br>3️⃣ Trade saved as new version.                                                         |
| **SentToCounterparty**     | **Book**          | SentToCounterparty → Executed     | Requester or Approver UserId + Confirmation | 1️⃣ Both Requester and Approver can book.<br>2️⃣ No re-validation.<br>3️⃣ Trade saved as new version.                                                                        |
| **SentToCounterparty**     | **Cancel**        | SentToCounterparty → Cancelled    | Requester or Approver UserId                | 1️⃣ Both Requester and Approver can cancel.<br>2️⃣ Trade saved as new version.                                                                                               |

