Funko-Pop-Watch
==============
.. contents:: :depth: 1

Description
----------

 **NOTE: will only work on fixes as I have time. This is just a small script to get a Pop I need.** This is a script to scrape funko pop websites to check for item availability. It sends notification via the app "Telegram". 

Running the utility from command line
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

	python pop_bot.py


Requirements
----------
 This program requires you install the app "Telegram". Then you will need to create an API token. Instruction on how to do that can be found here: https://core.telegram.org/bots#6-botfather

Usage
----------
 1. Obtain a telegram API token following the following steps: https://core.telegram.org/bots#6-botfather
 2. Obtain the channel id by sending a message from the channel you want to use and then runnign the following command.
   a. curl https://api.telegram.org/bot[TELEGRAM_TOKEN]/getUpdates -v
   b. This will give you the channel id to use in the code
 3. Then you can either run the included executable or running the code directly.
 4. Set *Environement Variable* -> **POPENV** to "dev", "stg", or "prd"
   a. **dev** sets the quantity to purchase to 1, chrome options to have '--headless' *DISABLED*, and **DOES NOT PERFORM AUTOCHECKOUT**
   b. **stg** sets the quantity to purchase to 3, chrome options to have '--headless' *DISABLED*, and **DOES PERFORM AUTOCHECKOUT**
   c. **prd** sets the quantity to purchase to 5, chrome options to have '--headless' *ENABLED*, and **DOES PERFORM AUTOCHECKOUT**

Bot Usage
----------
 1. /start - starts the search for the specific funko pops
 2. /stop - stops the bot from searching funko pops
 3. /add - takes a single parameter <url> and adds it to the search list
 4. /delete - tales a single parameter <url> and deleted the item if it exists in the search list
 5. /list - shows you the entire search list.
 6. /help - :)

Contributing
----------

 1. Fork it!
 2. Create your feature branch: `git checkout -b my-new-feature`
 3. Commit your changes: `git commit -am 'Add some feature'`
 4. Push to the branch: `git push origin my-new-feature`
 5. Submit a pull request :D

History
----------

  * 11/04/2018: Initial Commit
  * 11/04/2018: Added support for the following stores
	- Hot Topic
	- Box Lunch
	- Walmart
	- Barnes and Noble
	- GameStop
	- Blizzard
	- Gemini Collectibles
	- Target
  * 11/08/2018: Added readme, requirements and made code readable
  * 04/18/2019: View Following this [Pull Request](https://github.com/LumbaJack/Funko_Pop_Watcher/pull/2)

License
---------------------

License: Apache 2.0 License
