let randomNumber=Math.floor(Math.random()*100)+1

const guesses=document.querySelector('.guesses')
const lastResult=document.querySelector('.lastResult')
const lowHigh=document.querySelector('.lowHigh')

const guessSubmit=document.querySelector('.guessSubmit')
const guessField=document.querySelector('.guessField')

let guessCount=1;
let resetButton;

function check() {
   const userGuess=Number(guessField.value);
   if (guessCount==1) {
      guesses.textContent='previous guesses: ';
   }

   if (userGuess==randomNumber) {
      lastResult.textContent='Congratulations!';
      lastResult.style.backgroundColor='green';
      lowHigh.textContent='';
      console.log('guessed right');
      setGameOver();
   }
   else if (userGuess>randomNumber) {
      lastResult.textContent='Too high!';
      lastResult.style.backgroundColor='red';
      lowHigh.textContent='high';
      console.log('too high');
      guesses.textContent+=`${userGuess}`;
   }
   else if (userGuess<randomNumber) {
      lastResult.textContent='Too low!';
      lastResult.style.backgroundColor='red';
      lowHigh.textContent='low';
      console.log('too low');
      guesses.textContent+=`${userGuess}`;
   }
   else if (guessCount==10) {
      lastResult.textContent='Exceeded number of attempts';
      lastResult.style.backgroundColor='red';
      lowHigh.textContent='';
      setGameOver();
   }
   guessCount++;
   guessField.value='';
   guessField.focus();
}

function setGameOver(){
   guessField.disabled=true;
   guessSubmit.disabled=true;
   resetButton=document.createElement('button');
   resetButton.textContent='New game';
   document.body.append(resetButton);
   resetButton.addEventListener('click',resetGame);
}

function resetGame() {
   guessCount=1;
   const resetParas=document.querySelectorAll('.resultParas p');
}


guessSubmit.addEventListener('click',check);