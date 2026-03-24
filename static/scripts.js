function usingRange() {
    for (const input in document.getElementsByClassName('range')) {
        document.getElementsByClassName('range')[input].style.cursor = "grabbing"
    }
}

function notUsingRange() {
    for (const input in document.getElementsByClassName('range')) {
        document.getElementsByClassName('range')[input].style.cursor = "grab"
    }
}

function countryFinder(text) {
    let checkboxes = document.getElementsByClassName('answer_checkbox')
    let labels = document.getElementsByClassName('countryNames')

    for (let i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i].value.toLowerCase().includes(text.toLowerCase())) {
            checkboxes[i].style.visibility = "visible"
            labels[i].style.visibility = "visible"
        } else {
            checkboxes[i].style.visibility = "hidden"
            labels[i].style.visibility = "hidden"
        }
    }
}

function checkTheBoxes(maxAmount, name) {
    if (document.getElementsByName(name)[0].checked) {
        document.getElementsByName(name)[0].checked = false
    } else {
        document.getElementsByName(name)[0].checked = true
    }

    let checkedBoxes = []
    let checkboxes = document.getElementsByClassName('answer_checkbox')
    let thisCheckbox = document.getElementsByName(name)[0]

    for (let i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i].checked) {
            checkedBoxes.push(i)
        }
        switch (maxAmount) {
            case 1:
                checkboxes[i].checked = false
                thisCheckbox.checked = true
                break;
            case 2:
                if (checkedBoxes.length > maxAmount) {
                    if (checkboxes[checkedBoxes[maxAmount]] === thisCheckbox) {
                        checkboxes[checkedBoxes[0]].checked = false
                    }
                    if (checkboxes[checkedBoxes[0]] === thisCheckbox || checkboxes[checkedBoxes[1]] === thisCheckbox) {
                        checkboxes[checkedBoxes[maxAmount]].checked = false
                    }
                }
                break;

            case 3:
                if (checkedBoxes.length > maxAmount) {
                    if (checkboxes[checkedBoxes[maxAmount]] === thisCheckbox || checkboxes[checkedBoxes[maxAmount - 1]] === thisCheckbox) {
                        checkboxes[checkedBoxes[0]].checked = false
                    }
                    if (checkboxes[checkedBoxes[0]] === thisCheckbox || checkboxes[checkedBoxes[1]] === thisCheckbox) {
                        checkboxes[checkedBoxes[maxAmount]].checked = false
                    }
                }
                break;
            default:
                break;
        }
    }
}

function clearTheTable(yesOrNo) {
    //console.log(yesOrNo)
    if (yesOrNo === true) {
        window.open("/clear-the-scoreboard", "_blank")
        window.close()
    }
}

function inputRangePercentChange(value, labelId) {
    document.getElementById(labelId).innerText = value
}

function popUpWindow(answer) {

    let blockerDiv = document.createElement('div')
    let answerForm = document.getElementById('answer-form')
    let popUpDiv = document.createElement('div')
    let submit = document.createElement('input')
    let label = document.createElement('label')

    blockerDiv.setAttribute('id', 'blockerDiv')
    blockerDiv.setAttribute('class', 'transparent_box')

    label.setAttribute('class', 'titleLabel')
    label.innerText = "The answer was " + answer

    submit.setAttribute('type', 'submit')
    submit.setAttribute('name', 'answer-button')
    submit.setAttribute('class', 'regularButton')
    submit.setAttribute('value', 'Ok')

    popUpDiv.setAttribute('id', 'popUpDiv')
    popUpDiv.setAttribute('class', 'transparent_box')

    popUpDiv.append(label)
    popUpDiv.append(submit)

    blockerDiv.append(popUpDiv)
    answerForm.append(blockerDiv)
}

function customAlertPopUp() {
    let popUp = document.createElement("div")
    let label = document.createElement('label')
    let buttonsDiv = document.createElement("div")
    let okButton = document.createElement('button')
    let noButton = document.createElement('button')

    popUp.setAttribute('id', 'popUpDiv')
    popUp.setAttribute('class', 'transparent_box')

    label.innerText = "Are you sure?"
    label.setAttribute('class', 'titleLabel')
    popUp.append(label)

    buttonsDiv.setAttribute('class', 'buttonsDiv')
    popUp.append(buttonsDiv)

    okButton.innerText = "Yes"
    noButton.innerText = "No"
    okButton.setAttribute('class', 'regularButton')
    noButton.setAttribute('class', 'regularButton')

    okButton.setAttribute('onclick', 'clearTheTable(true)')
    noButton.setAttribute('onclick', 'removeThePopUp()')

    buttonsDiv.append(okButton)
    buttonsDiv.append(noButton)

    document.body.append(popUp)
}

function removeThePopUp() {
    document.getElementById("popUpDiv").remove()
}

function randomizeMyProfilePicture(current_user_id, user_id){
    if (current_user_id === user_id){
        location.href = "/randomize-my-profile-picture"
    }
}