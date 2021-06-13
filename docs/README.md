# Telegram proposal bot

Bot for creating PDF file from styled HTML. User can fill the document fields via Telegram bot and get a PDF as an output.

[Expected vs. fact PDF comparison](https://github.com/vladhutsal/HTMLtoPDF_TelegramBot/blob/master/docs/fact_vs_expected.png)

[Roadmap](https://github.com/vladhutsal/HTMLtoPDF_TelegramBot/blob/master/docs/roadmap.txt)

## How to read this?

Two parts:

**Overview** -  explain main bot's idea

**Flow example** - shows flow from the `/start` command to proposal's PDF.

>In case of questions write me on Telegram: @rotydoge

## Overview
[Google Docs Proposal template](http://bit.ly/UTOR_proposal_template)
#### There are four parts of proposal creation flow:
      1. Send your document using a Google Docs Proposal template
      2. Add additional info, answering bot's questions (e.g. Creation date or Deadlines)
      3. Choose engineer from an engineers list
      4. Add engineers rate for current proposal

Every iteration overs after you press button, that placed right to the `Edit info` button, at "What's next?" stage  (e.g. `Choose engineer` or `Continue`)

>**! NOTE:** After you've pressed this button - there is no going back, you need to restart bot using `/start` command and start over again. Pay attention on what are you doing.


#### What you can do:
* Choose between two modes - manual and auto, to create proposal through DOCX parsing or manualy type each title
* Edit info after each data-fill iteration, except the DOCX part
* Add new engineer to the database
* Generate test PDF to see if there everything works well
* Restart your bot to start over.

#### What you can't do:
* Edit data after choosing something on "What's next" stage
* Delete or edit current engineers
* Edit or change downloaded \*\.docx file

#### What you can do in the nearest future:
* Edit and delete engineers

## Flow example

#### Prerequisites:

Choose mode that fits better in `More..` menu.

If the button's text says `Current mode: manual`:
* You are in the manual mode and need to write all content right in the bot. The bot will show you a title, you need to answer with text (or photo, if bot asks for it).
* You can start from the **section 2** of this instruction.

If the button's text says `Current mode: with docx`:
* You are in the docx-parse mode.
* Start reading from **section 1.**

#### 1. You need to have your document with main content prepared. [Here is a template to work with](http://bit.ly/UTOR_proposal_template)

>**! NOTE:** be sure that the Headings style are set up, and all Headings goes in the right order:

    1. Main current goal
    2. Client expectations
    3. Next potential steps
    4. Type of provided services
    5. Report types
    6. Expected hours per week
    7. Value added

#### 2. Press `Create new proposal` button.

#### 3. Download your \*.docx file or follow bot's questions about main content (for manual mode).
Main content headers will be the same as for DOCX mode.

#### 4. Now bot will ask you to fill additional info in the next order:
    1. Prepared by              name of sales manager, who'll send proposal to the client
    2. Creation date            recommended to use date in "November 01, 2020" style
    3. Deadlines                "Longterm", "TBD" or date of deadline using the previous style recommendation
    4. Clinet's company name    is used only for pretty file naming

#### 5. If there was a mistake, you can edit your data using `Edit info` button.

#### 6. Click `Choose engineer` button and tap on the engineers name, who will take a part in the upcoming job.
The name will disappear and you'll see short pop-up sayng _"Engineer added"_

#### 7. If you see only `Add new engineer` and `Continue` buttons:
that's mean that there are no saved engineers. You can add new one, by pressing `Add new engineer`. That engineer will be saved to the database and you be able to include him in any proposal you'll create in the future.

>**! NOTE:** the last part of adding new engineer - it's his photo.  
>When "Photo" title shows up, you need to send squares, not large photo to bot and it will be saved.
>You can edit engineer info only after adding. You can't edit or delete engineers after by yourself.
>You need to choose your freshly added engineer from engineers list again, by pressing "Choose engineer" button.

#### 8. After all engineers have been added, press `Continue` to set engineers rate in current proposal.
Write the hourly rate for an engineer, whose name bot asking. You don't need to use dollar sign.

#### 9. If everything is alright - press `Creapte PDF`.

