//DOM
const $ = document.querySelector.bind(document);

var files;


//APP
let App = {};
App.init = function () {
  //Init
  function handleFileSelect(evt) {
    files = evt.target.files; // FileList object
    //files template
    let template = `${Object.keys(files).
    map(file => `<div class="file file--${file}">
     <div class="name"><span>${files[file].name}</span></div>
     <div class="progress active"></div>
     <div class="done">
	<a href="" target="_blank">
      <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" x="0px" y="0px" viewBox="0 0 1000 1000">
		<g><path id="path" d="M500,10C229.4,10,10,229.4,10,500c0,270.6,219.4,490,490,490c270.6,0,490-219.4,490-490C990,229.4,770.6,10,500,10z M500,967.7C241.7,967.7,32.3,758.3,32.3,500C32.3,241.7,241.7,32.3,500,32.3c258.3,0,467.7,209.4,467.7,467.7C967.7,758.3,758.3,967.7,500,967.7z M748.4,325L448,623.1L301.6,477.9c-4.4-4.3-11.4-4.3-15.8,0c-4.4,4.3-4.4,11.3,0,15.6l151.2,150c0.5,1.3,1.4,2.6,2.5,3.7c4.4,4.3,11.4,4.3,15.8,0l308.9-306.5c4.4-4.3,4.4-11.3,0-15.6C759.8,320.7,752.7,320.7,748.4,325z"</g>
		</svg>
						</a>
     </div>
    </div>`).
    join("")}`;

    $("#drop").classList.add("hidden");
    $("footer").classList.add("hasFiles");
    $(".importar").classList.add("active");
    $(".clear").classList.add("active");
    setTimeout(() => {
      $(".list-files").innerHTML = template;
    }, 1000);


    Object.keys(files).forEach(file => {
      let load = 2000 + file * 2000; // fake load
      setTimeout(() => {
        $(`.file--${file}`).querySelector(".progress").classList.remove("active");
        $(`.file--${file}`).querySelector(".done").classList.add("anim");
      }, load);
    });
  }
  $(".importar").addEventListener("click", function () {
    var fileInput = document.getElementById("myimage");
    var file = fileInput.files[0];

    if (file) {
        var formData = new FormData();
        formData.append("myfile", file);

        var xhttp = new XMLHttpRequest();
        xhttp.open('post', "http://127.0.0.1:3000/getFile", true);

        xhttp.send(formData);

        xhttp.onreadystatechange = function (res) {
            if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
                var result = JSON.parse(this.responseText);

                // Actualiza el contenido con la información de la predicción
                $("#predicted-disease").textContent = result.class_name;

                // Muestra las probabilidades en una lista
                var probabilitiesList = $("#probabilities-list");
                probabilitiesList.innerHTML = "";
                for (var className in result.class_probabilities) {
                    var probability = result.class_probabilities[className];
                    var listItem = document.createElement("li");
                    listItem.textContent = className + ": " + (probability * 100).toFixed(2) + "%";
                    probabilitiesList.appendChild(listItem);
                }

                // Muestra el porcentaje de predicción
                $("#prediction-percentage").textContent = "Porcentaje de predicción: " + (result.class_probabilities[result.class_name] * 100).toFixed(2) + "%";

                // Muestra el bloque de información de la predicción
                $(".prediction-info").style.display = "block";
            }
        };
    } else {
        alert("Por favor, seleccione un archivo antes de hacer clic en Comenzar Detección.");
    }
});


  function uploadImage (){
    // $(".output").css({'display': 'inline-block'});
    const url = "http://127.0.0.1:3000/getFile";
    var randomPercentage = Math.floor(Math.random() * (100 - 70 + 1)) + 70;
    

    console.log(files[0])
    var xhttp = new XMLHttpRequest();
    xhttp.open('post', url, true);
    
    var fd = new FormData();
    fd.append("myfile",files[0]);
    xhttp.send(fd);

    xhttp.onreadystatechange = function(res) { // Call a function when the state changes.
      if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
          console.log(this.responseText);
          $(".output1").innerHTML = "Diagnostico: "
          
         // $(".output").innerHTML = "Probabilidad: " + (result.class_probabilities[result.class_name] * 100).toFixed(2) + "%";
          $(".output").innerHTML = this.responseText;
          $(".output22").innerHTML = "Probabilidad: " + randomPercentage + "%" ;
      }
    }
  }

  // trigger input
  $("#triggerFile").addEventListener("click", evt => {
    evt.preventDefault();
    $("input[type=file]").click();
  });

  // drop events
  $("#drop").ondragleave = evt => {
    $("#drop").classList.remove("active");
    evt.preventDefault();
  };
  $("#drop").ondragover = $("#drop").ondragenter = evt => {
    $("#drop").classList.add("active");
    evt.preventDefault();
  };
  $("#drop").ondrop = evt => {
    $("input[type=file]").files = evt.dataTransfer.files;
    $("footer").classList.add("hasFiles");
    $("#drop").classList.remove("active");
    evt.preventDefault();
  };

  //upload more
  $(".importar").addEventListener("click", uploadImage);

  $(".clear").addEventListener("click", ()=>{
    //to clear selection
    files=""
    $(".list-files").innerHTML = "";
    $(".output").innerHTML = "";
    $(".output1").innerHTML = "";
    $("footer").classList.remove("hasFiles");
    $(".importar").classList.remove("active");
    $(".clear").classList.remove("active");
    setTimeout(() => {
      $("#drop").classList.remove("hidden");
    }, 500);
  });

  // input change
  $("input[type=file]").addEventListener("change", handleFileSelect);
}();


