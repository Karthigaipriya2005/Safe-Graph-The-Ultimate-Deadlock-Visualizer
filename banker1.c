#include <stdio.h>
#include <stdbool.h>

#define MAX_P 10  // Maximum number of processes
#define MAX_R 10  // Maximum number of resources

int main() {
    int n, m;
    scanf("%d %d", &n, &m);  // Number of processes (n) and resources (m)

    // Declare matrices for allocation, max, available, need, and finish
    int alloc[MAX_P][MAX_R], max[MAX_P][MAX_R], avail[MAX_R];
    int need[MAX_P][MAX_R], finish[MAX_P] = {0};  // finish array to track completed processes
    int safeSeq[MAX_P], count = 0;  // Array to store safe sequence and count of completed processes

    // Input Allocation Matrix
    printf("Enter Allocation matrix (n x m):\n");
    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++)
            scanf("%d", &alloc[i][j]);

    // Input Max Matrix
    printf("Enter Max matrix (n x m):\n");
    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++)
            scanf("%d", &max[i][j]);

    // Input Available Resources
    printf("Enter Available resources (m):\n");
    for (int i = 0; i < m; i++)
        scanf("%d", &avail[i]);

    // Calculate Need Matrix (Need = Max - Allocation)
    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++)
            need[i][j] = max[i][j] - alloc[i][j];

    // Banker's Algorithm with dynamic checking and revisiting rejected processes
    while (count < n) {  // Repeat until all processes are completed
        bool found = false;
        
        // Check all processes in a single round
        for (int i = 0; i < n; i++) {
            if (!finish[i]) {  // Process has not finished yet
                bool canRun = true;

                // Check if the process can run (need <= available resources)
                for (int j = 0; j < m; j++) {
                    if (need[i][j] < 0 || need[i][j] > avail[j]) {
                        canRun = false;
                        break;
                    }
                }

                // If process can run, allocate resources and mark process as finished
                if (canRun) {
                    for (int j = 0; j < m; j++) {
                        avail[j] += alloc[i][j];  // Resources are released after the process finishes
                    }

                    safeSeq[count++] = i;  // Store the process number in safe sequence
                    finish[i] = 1;  // Mark process as finished
                    found = true;  // A process was found that can run
                }
            }
        }

        // If no process was found that can execute in this round, break (deadlock detected)
        if (!found) {
            break;  // If no process was found to execute in a full pass, we are deadlocked
        }
    }

    // Print Safe Sequence (if found)
    printf("Safe Sequence: ");
    for (int i = 0; i < count; i++) {
        printf("P%d ", safeSeq[i]);
    }
    printf("\n");

    // If not all processes finished, detect deadlock
    if (count < n) {
        printf("Deadlock detected among: ");
        for (int i = 0; i < n; i++) {
            if (!finish[i]) {  // Process is not finished
                printf("P%d ", i);
            }
        }
        printf("\n");
    }

    return 0;
}