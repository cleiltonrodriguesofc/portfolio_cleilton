document.addEventListener('DOMContentLoaded', function () {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);


  // By default, load the inbox
  load_mailbox('inbox');

  // call compose-form to get email data and send it
  document.querySelector('#compose-form').addEventListener('submit', send_email);
  document.querySelector('#compose-reply').addEventListener('submit', send_reply);


  // toggle menu buttons to hide or unhide
  document.querySelector('#menu-button').addEventListener('click', () => {
    const menu = document.querySelector('.button');

    if (menu.style.display === 'none') {
      menu.style.display = 'block'
    } else {
      menu.style.display = 'none'
      window.addEventListener('resize', () => {
        // hide names
        if (window.innerWidth < 650) {
          document.querySelector('#inbox').innerHTML = '...';
          document.querySelector('#compose').innerHTML = '...';
          document.querySelector('#sent').innerHTML = '...';
          document.querySelector('#archived').innerHTML = '...';
          document.querySelector('#menu-button').innerHTML = '☰';
        } else {
          // show names
          document.querySelector('#inbox').innerHTML = 'Inbox';
          document.querySelector('#compose').innerHTML = 'Compose';
          document.querySelector('#sent').innerHTML = 'Sent';
          document.querySelector('#archived').innerHTML = 'Archived';
          document.querySelector('#menu-button').innerHTML = '☰ Menu';
        }
      })
    }
  })

});




function compose_email() {
  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';


}


// load mail box for required box
function load_mailbox(mailbox) {

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // call fetch to get emails 
  fetch(`/projetos/mail/emails/${mailbox}`)
    // convert response to json
    .then(response => response.json())
    .then(emails => {



      // loop through each email and display it
      emails.forEach(email => {

        // create div for each email
        const emailDiv = document.createElement('div');
        emailDiv.className = 'email-item';


        // render sent email on sent box
        if (mailbox === 'sent') {
          emailDiv.innerHTML = `
        ${email.recipients} - ${email.subject}
        <span class"timestamp" style="float: right;">${email.timestamp}</span>
      `;
        }
        // render received emails on inbox
        if (mailbox === 'inbox') {
          emailDiv.innerHTML = `
        ${email.sender} - ${email.subject}
        <span class"timestamp" style="float: right;">${email.timestamp}</span>
      `;
        }
        if (mailbox === 'archive') {
          emailDiv.innerHTML = `
        ${email.sender} - ${email.subject}
        <span class"timestamp" style="float: right;">${email.timestamp}</span>
      `;
        }

        // toggle color between read and unread email
        if (email.read) {
          emailDiv.style.backgroundColor = 'gray';
          emailDiv.style.color = 'white';
        } else {
          emailDiv.style.fontWeight = 'bold'
          emailDiv.style.backgroundColor = 'white';
        }

        // add event to open email 
        emailDiv.addEventListener('click', () => {
          view_email(email.id, mailbox);
          // call read_email function too
          read_email(email.id);
        });


        // append email to emails view
        document.querySelector('#emails-view').appendChild(emailDiv);
      });

    });
}

// create function to send email
function send_email(event) {
  // prevent reloading page with preventDefault
  event.preventDefault();

  // get values from recipients, subject and body from email composed
  const recipients = document.querySelector('#compose-recipients').value;
  const subject = document.querySelector('#compose-subject').value;
  const body = document.querySelector('#compose-body').value;

  // call fetch to send email
  fetch('/projetos/mail/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: recipients, // email recipient
      subject: subject,
      body: body
    })
  })
    .then(response => response.json())
    .then(result => {


      // redirect to inbox
      load_mailbox('sent');

    });
}

// create a function to archive email
function archive_email(email_id) {
  fetch(`/projetos/mail/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
      archived: true
    })
  })
    .then(() => {

      // redirect to inbox
      load_mailbox('inbox');
    }
    )
}

// un-archive email
function unarchive_email(email_id) {
  fetch(`/projetos/mail/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
      archived: false
    })
  })
    .then(() => {
      load_mailbox('inbox')
    })
}

// function to mark as read
function read_email(email_id) {

  fetch(`/projetos/mail/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
      read: true
    })
  })
    .then(() => {

    })
}
// function unread
function unread_email(email_id) {

  fetch(`/projetos/mail/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
      read: false
    })
  })
    .then(() => {

    })
}

// create function to show email.id
function view_email(email_id) {

  // get email id with fetch
  fetch(`/projetos/mail/emails/${email_id}`)
    .then(response => response.json())
    .then(email => {


      // create div for each email
      const emailDiv = document.createElement('div');
      emailDiv.className = 'view-email-item';

      // render email on archive and inbox
      emailDiv.innerHTML = `
    <div id="email-header">
      <div>
      <strong>From:</strong> ${email.sender}
      <span style="float: right;">${email.timestamp}</span>
      </div>
      
      <div>
        <strong>To:</strong> ${email.recipients}
        
        <button class="btn btn-sm btn-outline-primary" style="float: right;"bottom: 0;" id="archive_email"></button>

        <button class="btn btn-sm btn-outline-primary" style="float: right;"bottom: 0;" id="unread">Unread</button>

      
      </div>
      <div>
        <strong>Subject:</strong> ${email.subject}
      </div>
    </div>
        
    <hr>
    <div id="email-body">
      ${email.body} 
    </div>
    <hr>
    
    <div id="div-reply">
      <button class="btn btn-sm btn-outline-primary" style="bottom: 0;" id="reply">Reply</button>
    </div>
    `;
      // display email and hide emails
      document.querySelector('#emails-view').innerHTML = "";
      document.querySelector('#emails-view').appendChild(emailDiv);

      // archive and un-archive email calling the functions
      const archiveButton = document.querySelector('#archive_email');


      // hide archive button on sent box
      // get username element
      const usernameElement = document.querySelector('.username');
      // call username content
      const loggedInUser = usernameElement ? usernameElement.textContent.trim() : null;
      // hide archive button on sent email
      if (email.sender === loggedInUser) {

        archiveButton.style.display = 'none';
      }
      if (email.archived) {
        archiveButton.innerHTML = 'Unarchive'
        archiveButton.onclick = () => unarchive_email(email.id);
      } else {
        // Call archive email function
        archiveButton.innerHTML = 'Archive';
        archiveButton.onclick = () => archive_email(email.id);
      }
      // call unread function
      document.querySelector('#unread').addEventListener('click', () => unread_email(email.id));
      // Call reply email function
      document.querySelector('#reply').addEventListener('click', () => reply_email(email.id));


    });
}

// create a function to reply email
function reply_email(email_id) {
  const replyForm = document.querySelector('#reply-view');
  const replyButton = document.querySelector('#reply');
  const replyRecipients = document.querySelector('#compose-reply-recipients');
  const replySubject = document.querySelector('#compose-reply-subject');
  const replyBody = document.querySelector('#compose-reply-body');
  // get email informations
  fetch(`/projetos/mail/emails/${email_id}`)
    .then(response => response.json())
    .then(email => {


      // first I need to render the form to reply
      if (replyForm.style.display === 'none') {
        replyForm.style.display = 'block';
        replyButton.style.display = 'none';
        // render email values
        replyRecipients.value = `${email.sender}`;

        // check Re: in subject and do not include it if already exists
        // use trim() to cut it
        if (email.subject.trim().startsWith('Re:')) {
          replySubject.value = email.subject.trim();
        } else {
          replySubject.value = `Re: ${email.subject.trim()}`;
        }

        // render form with a value
        replyBody.value = `
      
          
    ------------------------------------------------------------------------------------------------------------
    On ${email.timestamp} ${email.sender} wrote:
    ------------------------------------------------------------------------------------------------------------
    ${email.body}
    
    `
      }
      else {
        replyForm.style.display = 'none';
        replyButton.style.display = 'block';
      }

      // Now, hide form
      document.querySelector('#reply-submit').addEventListener('click', () => {
        replyForm.style.display = 'none';
        replyButton.style.display = 'block';
      });
      document.querySelector('.sidebar-buttons').addEventListener('click', () => {
        replyForm.style.display = 'none';
        replyButton.style.display = 'block';
      });


    })
}
function send_reply(event) {
  event.preventDefault();
  const replyRecipients = document.querySelector('#compose-reply-recipients');
  const replySubject = document.querySelector('#compose-reply-subject');
  const replyBody = document.querySelector('#compose-reply-body');
  fetch('/projetos/mail/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: replyRecipients.value,
      subject: replySubject.value,
      body: replyBody.value
    })
  })
    .then(response => response.json())
    .then(result => {

      load_mailbox('sent')
    })
}