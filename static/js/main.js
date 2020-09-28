// if there was a task and user left the page
// he never knew whether task had been completed or not
// so this functions takes tasks in localStorage
// and figures what the task result is 
// and displays it to the user whatever page he is on
// should run once DomContentLoaded
function lookForUnresolvedTasks(){
  for (let i=0; i<localStorage.length; i++){
    let current = localStorage.key(i);
    if (current.includes('task')){
      // There's a task user has no idea about
      taskController(current, localStorage.getItem(current));
    }
  }
}

function taskController(taskKeyName, taskId){
  let timeoutID = setTimeout(function tick(){
    fetch('/api/accounts/task_check/', {
      method: "POST",
      headers: {
        'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest',
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': getCookie('csrftoken'),
        'Content-Type': 'application/json',
      }, 
      body: JSON.stringify({"task_id": taskId})
    }).then(response => {
      if (response.ok){ 
        response.json().then(data => {
          status = data['status'];
          result = data['result'];
          if (status === 'PENDING'){
            setTimeout(tick, 5000);
          } else {
            clearTimeout(timeoutID);
            localStorage.removeItem(taskKeyName);
            updateUiWithTaskResult(status, result);
          }
        }).catch(err => {console.log(err)})
      } else {
        response.json().then(errData => { 
          console.log(errData);
        }).catch(err => {console.log(err)})
      }
    }).catch(err => {console.log('never here, but just in case!')});
  }, 5000)
}

function detailedTaskController(taskKeyName, taskId){
  let timeoutID = setTimeout(function tick(){
    fetch('/api/accounts/task_check/', {
      method: "POST",
      headers: {
        'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest',
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': getCookie('csrftoken'),
        'Content-Type': 'application/json',
      }, 
      body: JSON.stringify({"task_id": taskId})
    }).then(response => {
      if (response.ok){ 
        response.json().then(data => {
          status = data['status'];
          result = data['result'];
          if (status === 'PENDING'){
            setTimeout(tick, 5000);
          } else {
            clearTimeout(timeoutID);
            localStorage.removeItem(taskKeyName);
            let contentDiv = document.querySelector('.content');
            contentDiv.innerHTML = '';
            contentDiv.insertAdjacentHTML('afterbegin', result);
            contentDiv.classList.remove('text-center');
            contentDiv.classList.add('text-left');
            document.querySelectorAll('.content div').forEach(div => div.removeAttribute('style'));
            document.querySelectorAll('br + br').forEach(br => br.remove());
          }
        }).catch(err => {console.log(err)})
      } else {
        response.json().then(errData => { 
          console.log(errData);
        }).catch(err => {console.log(err)})
      }
    }).catch(err => {console.log('never here, but just in case!')});
  }, 1000)
}

// You reall gotta make sure that each page has main .container
// Would have been so much easier using react tho
function updateUiWithTaskResult(status, result="NOT DONE YET"){
  let mainContainer = document.querySelector('main .container');
  if (!mainContainer) return;
  let informer = mainContainer.querySelector('.informer-peding');
  if (status === 'PENDING'){
    if (informer) return;
    mainContainer.insertAdjacentHTML('afterbegin',
     `<div class="row mt-4 informer-peding">
        <div class="col-md-12 px-0 mx-auto">
          <div class="alert alert-primary">You feed is loading, once done, you will get notified! ;)</div>  
        </div>
      </div>`);
  } else if (status === 'SUCCESS'){
    if (informer){
      informer.remove();
    }
    mainContainer.insertAdjacentHTML('afterbegin',
     `<div class="row mt-4 informer-peding">
        <div class="col-md-12 px-0 mx-auto">
          <div class="alert alert-primary" id='notifier'></div>  
        </div>
      </div>`);
    setTimeout(() => {
      try {
        let notifier = document.getElementById('notifier');
        if (result.length > 100){
          // meaning you probably scraped the article full content before
          // and you don't want your page to be ruined
          notifier.textContent = 'Your article\'s full content has been scraped!';
          return;
        }
        notifier.textContent = result;
      } catch (error) {
        console.log(error); 
      }
    }, 0);
  }
}

function create_html(data){
  let mainEl = document.body.querySelector('.content');
  mainEl.innerHTML = '';
  for (let piece of data){
    let mediaDiv = document.createElement('div');
    let mediaBodyDiv = document.createElement('div');
    let titleH5 = document.createElement('a');
    let contentP = document.createElement('p');
    let linkA = document.createElement('a');
    mediaDiv.classList.add('media', 'mb-4');
    mediaBodyDiv.classList.add('media-body', 'p-2', 'text-white');
    titleH5.classList.add('mb-2');
    contentP.classList.add('mb-2');
    linkA.classList.add('btn', 'btn-light');
    titleH5.textContent = piece.title;
    titleH5.setAttribute('href', '/posts/' + piece.id);
    if (piece.source === 'vc'){
      let div = document.createElement('div');
      div.insertAdjacentHTML('afterbegin', piece.content);
      div.querySelectorAll("figure").forEach(el => el.remove());
      div.querySelectorAll("img").forEach(el => el.remove());
      div.querySelectorAll("video").forEach(el => el.remove());
      div.querySelectorAll("script").forEach(el => el.remove());
      contentP.append(div);
    } else {
      contentP.textContent = piece.content.slice(0, 697) + '...'; 
    }
    linkA.setAttribute('href', piece.link);
    linkA.innerText = 'Read Original';

    mediaBodyDiv.append(titleH5, contentP, linkA)
    mediaDiv.append(mediaBodyDiv);
    mainEl.append(mediaDiv);
  }
}