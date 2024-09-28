////////////////////////////////////////////////////////////////////////////////
// Main File:        check_sudoku_board.c
// This File:        check_sudoku_board.c
// Other Files:      (name of all other files if any)
// Semester:         CS 354 Lecture 003 Fall 2023
// Grade Group:      gg19  (See canvas.wisc.edu/groups for your gg#)
// Instructor:       Mahmood
// 
// Author:           Sojung Lee
// Email:            lee2353@wisc.edu
// CS Login:         sojung
//
///////////////////////////  OPTIONAL WORK LOG  //////////////////////////////
//  Document your work sessions here or on your copy http://tiny.cc/work-log
//  Keep track of commands, structures, code that you have learned.
//  This will help you focus your review on this from each program that
//  are new to you. There is no need to submit work log.
/////////////////////////// OTHER SOURCES OF HELP ////////////////////////////// 
// Persons:          Identify persons by name, relationship to you, and email.
//                   Describe in detail the the ideas and help they provided.
//
// Online sources:   avoid web searches to solve your problems, but if you do
//                   search, be sure to include Web URLs and description of 
//                   of any information you find.
// 
// AI chats:         save a transcript and submit with project.
///////////////////////////////////////////////////////////////////////////////
// Copyright 2021-24 Deb Deppeler
// Posting or sharing this file is prohibited, including any changes/additions.
//
// We have provided comments and structure for this program to help you get
// started.  Later programs will not provide the same level of commenting,
// rather you will be expected to add same level of comments to your work.
////////////////////////////////////////////////////////////////////////////////

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char* DELIM = ",";  // commas ',' are a common delimiter character for data strings

/* TODO: implement this function
 * Returns 1 if and only if the 2D array of ints in board
 * is in a valid Sudoku board state.  Otherwise returns 0.
 *
 * DOES NOT PRODUCES ANY PRINTED OUTPUT
 *
 * A valid row or column contains only blanks or the digits 1-size,
 * with no duplicate digits, where size is the value 1 to 9.
 *
 * Note: This function requires only that each row and each column are valid.
 *
 * board: heap allocated 2D array of integers
 * size:  number of rows and columns in the board
 */
int valid_sudoku_board(int** board, int size) {
    if (1 <= size && size <= 9) { // check whether the size is betweeen value 1 to 9
        // check rows
        for (int i = 0; i < size; i++) {
            // array to check duplicates
            int* rowSet = malloc(sizeof(int) * (size + 1)); //size+1, so that directly store the number to the index 
            if (rowSet == NULL) {
                return 1; // Return 1 on memory allocation failure
            }
            // Initialize all elements to 0
            for (int k = 0; k < size+1; k++) {
                *(rowSet+k) = 0;  // Set each element to 0
            }
            // Check each number in the row
            for (int j = 0; j < size; j++) {
                int num = *(*(board+i)+j); // Get the current number
                if(0 <= num && num <= size){ // Elements should be value within 0 to size
                    if (num != 0) {  // Skip blanks (0 represents blank)
                        if (*(rowSet+num) == 1) {
                            return 1;  // Duplicate found in the row
                        }
                        *(rowSet + num) = 1;  // Mark the number as seen
                    }
                }
                else {
                    return 1; // array elements are not within 0 to 9
                }
            }
	    free(rowSet);
        }
        // check columns
        for (int j = 0; j < size; j++) {
            // array to check duplicates
            int* colSet = malloc(sizeof(int) * (size + 1)); //size+1, so that directly store the number to the index 
            if (colSet == NULL) {
                return 1; // Return 1 on memory allocation failure
            }// Initialize all elements to 0
            for (int k = 0; k < size+1; k++) {
                *(colSet + k) = 0;  // Set each element to 0
            }            
            // Check each number in the column
            for (int i = 0; i < size; i++) { // Get the current number
                int num = *(*(board + i) + j);
                if (0 <= num && num <= size) { // Elements should be value within 0 to size
                    if (num != 0) {  // Skip blanks
                        if (*(colSet + num) == 1) {
                            return 1;  // Duplicate found in the column
                        }
                        *(colSet + num) = 1;  // Mark the number as seen
                    }
                }
                else {
                    return 1; // array elements are not within 0 to 9
                }
            }
	    free(colSet);
        }
        return 0;  // No duplicates found in any rows and columns
    }
    else {
        return 1; // size is not within 1 to 9
    }
}

/* COMPLETED (DO NOT EDIT)
 * Read the first line of file to get the size of that board.
 *
 * PRE-CONDITION #1: file exists
 * PRE-CONDITION #2: first line of file contains valid non-zero integer value
 *
 * fptr: file pointer for the board's input file
 * size: a pointer to an int to store the size
 *
 * POST-CONDITION: the integer whos address is passed in as size (int *)
 * will now have the size (number of rows and cols) of the board being checked.
 */
void get_board_size(FILE* fptr, int* size) {
    char* line = NULL;
    size_t len = 0;

    // 'man getline' to learn about <stdio.h> getline
    if (getline(&line, &len, fptr) == -1) {
        printf("Error reading the input file.\n");
        free(line);
        exit(1);
    }

    char* size_chars = NULL;
    size_chars = strtok(line, DELIM); // 'man strtok' string tokenizer
    *size = atoi(size_chars);         // 'man atoi' alpha to integer
    free(line);                       // free memory allocated for line
}


/* TODO: COMPLETE THE MAIN FUNCTION
 * This program prints "valid" (without quotes) if the input file contains
 * a valid state of a Sudoku puzzle board wrt to rows and columns only.
 * It prints "invalid" (without quotes) if the input file is not valid.
 *
 * Usage: A single CLA that is the name of a file that contains data.
 *
 * argc: the number of command line args (CLAs)
 * argv: the CLA strings, includes the program name
 *
 * Returns 0 if file exists and is readable.
 * Exit with any non-zero result if unable to open and read the file given.
 */
int main(int argc, char** argv) {

    // TODO: Check if number of command-line arguments is correct.
    if (argc != 2) { 
        printf("Usage: ./check_sudoku_board <input_filename>\n");
        exit(1); // Exit with error if the argument count is incorrect
    }


    // Open the file
    FILE* fp = fopen(*(argv + 1), "r");
    if (fp == NULL) {
        printf("Can't open file for reading.\n");
        exit(1);
    }

    // will store the board's size, number of rows and columns
    int size;

    // TODO: Call get_board_size to read first line of file as the board size.
    get_board_size(fp, &size);

    // TODO: Dynamically allocate a 2D array for given board size.
    // You must dyamically create a array of pointers to other arrays of ints
    int** array;
    array = malloc(sizeof(int*) * size); //number of rows
    for (int j = 0; j < size; j++) {
        *(array + j) = malloc(sizeof(int) * size); //number of columns
    }

    // Read the remaining lines of the board data file.
    // Tokenize each line and store the values in your 2D array.
    char* line = NULL;
    size_t len = 0;
    char* token = NULL;
    for (int i = 0; i < size; i++) {

        // read the line
        if (getline(&line, &len, fp) == -1) {
            printf("Error while reading line %i of the file.\n", i + 2);
            exit(1);
        }

        token = strtok(line, DELIM);
        for (int j = 0; j < size; j++) {
            // TODO: Complete the line of code below
            // to initialize elements of your 2D array.
            *(*(array+i)+j) = atoi(token); // This fills the board with numbers
            // Move to the next value in the line (next column value)
            token = strtok(NULL, DELIM);
        }
    }

    // TODO: Call valid_sudoku_board and print the appropriate
    //       output depending on the function's return value.
    int result = valid_sudoku_board(array, size);
    if (result == 0) {
        printf("valid\n"); // Board is valid
    }
    else {
        printf("invalid\n"); // Board has duplicates or invalid entries
    }

    // TODO: Free dynamically allocated memory.
    for (int i = 0; i < size; i++) {
        free(*(array + i)); // Free each row
    }
    free(array); // Free the array of row pointers
    array = NULL; // Set pointer to NULL to avoid dangling pointer
    free(line); // Free the memory allocated for the line buffer

    //Close the file.
    if (fclose(fp) != 0) {
        printf("Error while closing the file.\n");
        exit(1);
    }

    return 0;
}
