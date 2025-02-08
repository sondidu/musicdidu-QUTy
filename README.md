# musicdidu-QUTY

A music player program designed for the [QUTy](https://cab202.github.io/quty/). You can create your own music by creating `.txt` files following a set of rules, and the board will play it for you! This project involves text validation through Python, custom code generation, and C code to play the music itself.

## How It Works
There is the [sheets](sheets/) directory, which holds all the music sheets in `.txt` file format. The `.txt` files are validated against a set of [rules](sheets/README.md). After all the sheets are validated, [music code](music%20code/README.md) is generated and stored in the board's flash by generating a `data.c` file in the [src/](src/) directory. If at least one of the sheets is invalid, then the build process fails, and errors are output to the terminal.

Music is played by initializing one of the TCBs to generate an interrupt every 1/24th of a beat called *ticks*. On each *tick*, it will either **keep playing the current note** or **look for the next note** by parsing the music codes. The cycle repeats until it reaches the end of the sheet.

## How To Use
Refer to the [sheets README](sheets/README.md) to see the validation rules and how to create your own music sheets.

After successfully building and uploading to your QUTy board, relevant information about the sheets is output to the terminal. Additionally, the music code of each sheet is created as files in the [music code/](music%20code/) directory for viewing.

Looking at the QUTy we initially enter the selection stage, and the 7-segment display will show the sheet number. Press **S1** and **S2** to decrement and increment the sheet number, respectively. The processed sheets are ordered alphabetically, and the terminal displays the number associated with each sheet.

After choosing a sheet, press **S3** to make a selection. The two decimal points in the 7-segment display will light up. Press **S4** to confirm the selection, and the music of the respective sheet will start playing. Press **S1**, **S2**, or **S3** to cancel the selection.

While music is playing, the 7-segment display will blink the left and right decimal points indicating the beats of the music. It will also constantly display the bar number. You can press **S3** to pause the music. After the music is paused, either press **S4** to continue playing or press **S2** to stop the music and return to the selection stage.

For more detailed information on validation rules and creating your own sheets, refer to the [sheets README](sheets/README.md).

For details on music code, refer to the [music code README](music%20code/README.md).
