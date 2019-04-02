# PASS
PASS is a Dutch data-to-text system for soccer reports. A description of the system can be found at https://www.aclweb.org/anthology/W17-3513 and an evaluation of the system's quality can be found at http://www.aclweb.org/anthology/C18-1082 . PASS consists of several modules:

- Topic collection module: collects topics from the match data and gives them a chronological order
- Lookup module: opens the template database and retrieves all the template categories and corresponding templates that could be used to describe an event
- Ruleset module: checks for each template category if the conditions to use said category have been matched
- Template selection module: selects a template from the possible templates in a weighted random fashion
- Governing module: walks through every topic in a stepwise order and interacts with all the other modules necessary to generate the text
- Text collection module: takes the text describing each event and combines them in a predetermined order
- Template filler module: empty slots in the templates are filled with the right kind of information
- Information variety module: ensures that certain types of information in the report will not be repeated
- Reference variety module: tries to spot the same referent in two subsequent sentences. If the module is able to find this, it will use
a different form to address the referent in the second sentence

You can find the templates for the win/loss and neutral conditions in Databases. The collected soccer data can be found in the InfoXMLs and NewInfoXMLs folders (Dutch Leagues 2015-16 COMPLETE2 gives more information about the data in InfoXMLs).

Only one library is needed to run PASS: BeautifulSoup (https://www.crummy.com/software/BeautifulSoup/bs4/doc/).
