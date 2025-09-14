function switchForm(action) {
    const forms = ['insert', 'update', 'delete'];
    forms.forEach(f => {
      document.getElementById(`${f}-form`).style.display = 'none';
    });

    document.getElementById(`${action}-form`).style.display = 'block';
    document.getElementById('form-title').innerText =
      action.charAt(0).toUpperCase() + action.slice(1) + ' Transaction';
  }

  function toggleCard() {
    const content = document.getElementById("cardContent");
    const btn = document.querySelector(".toggle-btn");

    if (content.style.display === "none") {
      content.style.display = "block";
      btn.textContent = "−";
    } else {
      content.style.display = "none";
      btn.textContent = "+";
    }
  }

  function loadTransaction(element) {
  switchForm('update');
  console.log("ID cargado:", element.dataset.id);
  document.getElementById('update-id').value = element.dataset.id;
  document.getElementById('update-description').value = element.dataset.description;
  document.getElementById('update-category').value = element.dataset.category;
  document.getElementById('update-amount').value = element.dataset.amount;
  document.getElementById('update-date').value = element.dataset.date;
}

function loadDelete(button) {
  switchForm('delete');
  const id = button.dataset.id;
  document.getElementById('delete-id').value = id;
}

document.addEventListener('DOMContentLoaded', () => {
  const img      = document.getElementById('graphic-image');
  const spinner  = document.getElementById('spinner');
  const buttons  = document.querySelectorAll('.filters button');
  let loading    = false;

  window.switchGraphic = switchGraphic;

  function switchGraphic(kind) {
    if (loading) return;
    loading = true;

    img.style.display     = 'none';
    spinner.style.display = 'inline-block';
    buttons.forEach(b => b.disabled = true);

    const seed      = img.dataset.seed;
    const timestamp = Math.floor(Date.now() / 1000);
    const url       = `/graphic/${seed}/${kind}.png?t=${timestamp}`;

    console.log('Loading Graph:', url);

    img.onload = () => {
      spinner.style.display = 'none';
      img.style.display     = 'block';
      buttons.forEach(b => b.disabled = false);
      loading = false;
    };
    img.onerror = () => {
      spinner.style.display = 'none';
      buttons.forEach(b => b.disabled = false);
      loading = false;
      console.error(`Error Loading Graph: ${url}`);
    };

    img.src = url;
  }

  buttons.forEach(btn =>
    btn.addEventListener('click', () =>
      switchGraphic(btn.dataset.kind)
    )
  );

  switchGraphic('balance');
  window.switchGraphic = switchGraphic;
});

document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('theme-toggle');
  const icon   = toggle.querySelector('i');

  // Aplica el tema guardado al cargar
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'dark') {
    document.body.classList.add('dark-mode');
    icon.classList.replace('bi-moon-fill', 'bi-sun-fill');
  }

  toggle.addEventListener('click', () => {
    const isDark = document.body.classList.toggle('dark-mode');

    // Cambia el icono
    if (isDark) {
      icon.classList.replace('bi-moon-fill', 'bi-sun-fill');
      localStorage.setItem('theme', 'dark');
    } else {
      icon.classList.replace('bi-sun-fill', 'bi-moon-fill');
      localStorage.setItem('theme', 'light');
    }
  });
});

document
  .getElementById('periodSelect')
  .addEventListener('change', ()=> {
    const select  =   document.getElementById('periodSelect');
    const img     =   document.getElementById('avgChartImg');
    const seed    =   img.dataset.seed
    const dwmy = select.value;
    const newSrc = `/dashboard/avg-expense-image/${dwmy}/${seed}/?` + Date.now();
    img.src = newSrc
    console.log('Loading Graph', newSrc);
});

function updateFreqChart() {
  const img      =   document.getElementById('freqChartImg');
  const seed     =   img.dataset.seed;
  const income   =   document.getElementById('incomeCheckbox').checked ? '1' : '0';
  const expense  =   document.getElementById('expenseCheckbox').checked ? '1' : '0';
  const ts       =   Date.now();
  const newSrc =`/dashboard/freq-categories-image/${seed}?income=${income}&expense=${expense}&ts=${ts}`;
  img.src = newSrc;
  console.log('Loading Graph', newSrc);
}

['incomeCheckbox','expenseCheckbox'].forEach(id =>
  document.getElementById(id).addEventListener('change', updateFreqChart)
);

function getCookie(name) {
  const cookies = document.cookie.split(';').map(c => c.trim());
  for (const c of cookies) {
    if (c.startsWith(name + '=')) {
      return decodeURIComponent(c.split('=')[1]);
    }
  }
  return null;
}

const pform = document.getElementById('category-predict-form');
pform.addEventListener('submit', async e => {
    e.preventDefault();
    const desc = document.getElementById('desc').value.trim();
    const seed = document.getElementById('seed')?.value || null;
    const csrftoken = getCookie('csrftoken');
    const resultDiv = document.getElementById('category-predict-result');

    console.log({ desc, seed, csrftoken });  

    const res = await fetch('api/category-predict/', {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      },
      body: JSON.stringify({ desc, seed })
    });

    const data = await res.json();
      if (res.ok) {
        resultDiv.innerHTML = 'Category: <strong>' + data.category + '</strong>';
      } else {
        resultDiv.textContent = 'Error: ' + data.error;
      }
});

const aform = document.getElementById('amount-predict-form');
aform.addEventListener('submit', async e => {
  e.preventDefault();
  const date = document.getElementById('predict-date').value;
  const seed = document.getElementById('seed')?.value || null;
  const token = getCookie('csrftoken');
  const params = new URLSearchParams({ date, seed });

  console.log(date,seed)

  const res = await fetch('api/amount-predict/', {
    method: 'POST',
    credentials: 'same-origin',
    headers: {
      'X-CSRFToken': token,
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: params.toString()
  });

  const data = await res.json();
  console.log('JSON Response', data)
  const target = document.getElementById('amount-predict-result');
  if (data.prediction !== undefined) {
    target.innerText = `Prediction: ${data.prediction} $ `;
  } else {
    target.innerText = `Error: ${data.error}`;
  }
});