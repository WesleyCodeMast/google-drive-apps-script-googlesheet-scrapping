code2report = """
function createNewGoogleDocs(sheetId) {
  //This value should be the id of your document template that we created in the last step
  const googleDocTemplate = DriveApp.getFileById('1X8KqPLSvHKWbezh0SbpADOhYKt_j4b2qQ_vOcWIYvG4'); // locate Google Doc this is the file path. This is the actual id of the document or template.
  debugger
  //This value should be the id of the folder where you want your completed documents stored
  const destinationFolder = DriveApp.getFolderById('1YJy5oE5MK-N7dsLDwne9TVmCVTxUC50V')
  //Here we store the sheet as a variable
  const sheet = SpreadsheetApp
    .openById(sheetId)
    .getSheetByName('Data')
    //this is the tab located within the excel document, on the bottom
 

    //Using the row data in a template literal, we make a copy of our template document in our destinationFolder

    const fullName = sheet.getRange("B10").getValue();

    const copy = googleDocTemplate.makeCopy(fullName + " PEPE Report" , destinationFolder) // rename file here
    //this is the name of the doc being created - using cell B10 + PEPE Report
    //Once we have the copy, we then open it using the DocumentApp
    const doc = DocumentApp.openById(copy.getId()) // opens file from Google doc
    //All of the content lives in the body, so we get that for editing
    const body = doc.getBody();
   
    //In these lines, we replace our replacement tokens with values from our spreadsheet row
    body.replaceText('{{first name1}}', sheet.getRange("B19").getValue().toUpperCase());
    body.replaceText('{{nickname}}', sheet.getRange("B22").getValue().toUpperCase());
    body.replaceText('{{middle name1}}', sheet.getRange("B20").getValue().toUpperCase());
    body.replaceText('{{last name1}}', sheet.getRange("B21").getValue().toUpperCase());
    body.replaceText('{{first name}}', sheet.getRange("B19").getValue());
    body.replaceText('{{last name}}', sheet.getRange("B21").getValue());
    body.replaceText('{{dob}}', sheet.getRange("B23").getValue());
    body.replaceText('{{position}}', sheet.getRange("B32").getValue());
    body.replaceText('{{hiring agency name}}', sheet.getRange("B2").getValue());
    body.replaceText('{{ethnicity}}', sheet.getRange("B34").getValue());
body.replaceText('{{age}}', sheet.getRange("B24").getValue());
body.replaceText('{{born location}}', sheet.getRange("B38").getValue());
body.replaceText('{{primarily raised}}', sheet.getRange("B39").getValue());
body.replaceText('{{currently lives}}', sheet.getRange("B30").getValue());
body.replaceText('{{parents}}', sheet.getRange("B40").getValue());
body.replaceText('{{college}}', sheet.getRange("B94").getValue());
body.replaceText('{{degree}}', sheet.getRange("B95").getValue());
body.replaceText('{{addlinedegree}}', sheet.getRange("B96").getValue());
    if(sheet.getRange("B26").getValue() == "He/Him"){
      body.replaceText('{{He/She}}',"He");
    body.replaceText('{{Him/Her}}', "Him");
    body.replaceText('{{His/Her}}', "His");
    body.replaceText('{{he/she}}', "he");
    body.replaceText('{{his/her}}', "his");
    body.replaceText('{{him/her}}', "him");
    body.replaceText('{{MrMs}}', "Mr.");
body.replaceText('{{male/female}}', "male");
    }
     if(sheet.getRange("B26").getValue() == "She/Her"){
      body.replaceText('{{He/She}}',"She");
    body.replaceText('{{Him/Her}}', "Her");
    body.replaceText('{{His/Her}}', "Her");
    body.replaceText('{{he/she}}', "she");
    body.replaceText('{{his/her}}', "her");
    body.replaceText('{{him/her}}', "her");
    body.replaceText('{{MrMs}}', "Ms.");
body.replaceText('{{male/female}}', "female");
     }
      if(sheet.getRange("B26").getValue() == "They/Them"){
      body.replaceText('{{He/She}}',"They");
    body.replaceText('{{Him/Her}}', "Them");
    body.replaceText('{{His/Her}}', "Their");
    body.replaceText('{{he/she}}', "they");
    body.replaceText('{{his/her}}', "Their");
    body.replaceText('{{him/her}}', "Them");
    body.replaceText('{{MrMs}}', "Mx.");
body.replaceText('{{male/female}}', "UNKNOWN");
     }
      if(sheet.getRange("B26").getValue() == "Other"){
      body.replaceText('{{He/She}}',"NnnHeShe");
    body.replaceText('{{Him/Her}}', "NnnHimHer");
    body.replaceText('{{His/Her}}', "NnnHis/Her");
    body.replaceText('{{him/her}}', "nnnhim/her");
    body.replaceText('{{his/her}}', "nnnhis/her");
    body.replaceText('{{him/her}}', "nnnhim/her");
    body.replaceText('{{MrMs}}', "NnnOther");
body.replaceText('{{male/female}}', "UNKNOWN");
     }
     if(sheet.getRange("B3").getValue() == "Sheriff's Office"){
      body.replaceText('{{agency}}',"Sheriff's Office");
     }
      if(sheet.getRange("B3").getValue() == "Police/Fire Department"){
      body.replaceText('{{agency}}',"department");
     }
       if(sheet.getRange("B3").getValue() == "All Other Agency Types (parole & probation, dispatch centers, etc.)"){
      body.replaceText('{{agency}}',"agency");
     }
if(sheet.getRange("B35").getValue() == "Yes"){
      body.replaceText('{{bilingual}}',"bilingual Spanish and English-speaking");
    }
     if(sheet.getRange("B35").getValue() == "No"){
      body.replaceText('{{bilingual}}',"monolingual English-speaking");
     }
  
  var headerSection = doc.getHeader(); // doc is Google doc, as noted at top of code
  
  // Modify the header content as needed
  var headerParagraphs = headerSection.getParagraphs();
  for (var i = 0; i < headerParagraphs.length; i++) {
    var paragraph = headerParagraphs[i];
// var text= paragraph.getText(); // retrieving the text of a singular paragraph - we deleted this because the paragraph had a built-in replace function.
   paragraph.replaceText('{{first name}}', sheet.getRange("B19").getValue());
   paragraph.replaceText('{{last name}}', sheet.getRange("B21").getValue());
if(sheet.getRange("B26").getValue() == "He/Him"){
   paragraph.replaceText('{{MrMs}}', "Mr.");
    }
     if(sheet.getRange("B26").getValue() == "She/Her"){
  paragraph.replaceText('{{MrMs}}', "Ms.");
     }
// paragraph.setText(text); // like you’re submitting it -- we deleted this because the paragraph had a built-in replace function - see above. can also do the following if I want to make a long comment in code -  /* then end with */
}

    //We make our changes permanent by saving and closing the document
    doc.saveAndClose();
    //Store the url of our new document in a variable
    const url = doc.getUrl();
    //Write that value back to the 'Document Link' column in the spreadsheet.
    //sheet.getRange(index + 1, 6).setValue(url)

}""".strip()

