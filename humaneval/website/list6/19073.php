<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta/css/bootstrap.min.css" integrity="sha384-/Y6pD6FV/Vv2HJnA6t+vslU6fwYXjCFtcEpHbNJ0lyAFsXTsjBbfaDjzALeQsN6M" crossorigin="anonymous">
  <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.11.0/umd/popper.min.js" integrity="sha384-b/U6ypiBEHpOf/4+1nzFpr53nxSS+GLCkfwBdFNTxtclqqenISfwAzpKaMNFNmj4" crossorigin="anonymous"></script>
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta/js/bootstrap.min.js" integrity="sha384-h0AbiXch4ZDo7tp9hKZ4TsHbi047NrKGLO3SEJAg45jXxnGIfYzk4Si90RDIqNm1" crossorigin="anonymous"></script>
  <!-- timer.js -->
  <script src="../js/timer.js"></script>
  <title>
   Semantic Data
 </title>
</head>
<body class="container">
  <br/>
  <header>
    <div class="row justify-content-center">
      <div class="col-6">
        <h5 class="text-center">Data</h5>
        <table class="table table-striped small">
          <tr>
            <td>BBC</td>
            <td><strong>keyPerson</strong></td>
            <td>Tony_Hall,_Baron_Hall_of_Birkenhead</td>
          </tr>
          <tr>
            <td>Bananaman</td>
            <td><strong>network</strong></td>
            <td>BBC</td>
          </tr>
          <tr>
            <td>BBC</td>
            <td><strong>locationCity</strong></td>
            <td>London</td>
          </tr>
        </table>
      </div>
    </div>
</header>
<div class="text-center" id="article">
  <h5 class="text-center">Summary</h5>
  <p class="lead" id="text_article">a key person at <span style="background-color: #FFFF00">the bbc</span> , which is located in <span style="background-color: #FFFF00">london</span> and broadcast <span style="background-color: #FFFF00">bananaman</span> , is <span style="background-color: #FFFF00">tony hall , baron hall of birkenhead</span> .</p>
</div>
<footer class="jumbotron text-center">
  <form action="../routing.php" method="post">
    <div class="form-group">
      <label>Fluency</label>
      <div class="radio">
        <label class="radio-inline">
          <strong>Very Bad</strong>
        </label>
        <label class="radio-inline" style="margin-left:0.5cm">
          <input type="radio" name="fluency" id="inlineRadio1" value="1"> 1
        </label>
        <label class="radio-inline" style="margin-left:0.5cm">
          <input type="radio" name="fluency" id="inlineRadio2" value="2"> 2
        </label>
        <label class="radio-inline" style="margin-left:0.5cm">
          <input type="radio" name="fluency" id="inlineRadio3" value="3"> 3
        </label>
        <label class="radio-inline" style="margin-left:0.5cm">
          <input type="radio" name="fluency" id="inlineRadio4" value="4" checked> 4
        </label>
        <label class="radio-inline" style="margin-left:0.5cm">
          <input type="radio" name="fluency" id="inlineRadio5" value="5"> 5
        </label>
        <label class="radio-inline" style="margin-left:0.5cm">
          <input type="radio" name="fluency" id="inlineRadio6" value="6"> 6
        </label>
        <label class="radio-inline" style="margin-left:0.5cm">
          <input type="radio" name="fluency" id="inlineRadio7" value="7"> 7
        </label>
        <label class="radio-inline" style="margin-left:0.5cm">
          <strong>Very Good</strong>
        </label>
      </div>
      <span class="form-text text-muted">Does the text flow in a natural, easy to read manner?</span>
    </div>
    <br>
    <div class="form-group">
      <label>Grammaticality</label>
      <div class="radio">
        <label class="radio-inline">
          <strong>Very Bad</strong>
        </label>
        <label class="radio-inline" style="margin-left:0.5cm">
          <input type="radio" name="grammar" id="inlineRadio1" value="1"> 1
        </label>
        <label class="radio-inline" style="margin-left:0.5cm">
          <input type="radio" name="grammar" id="inlineRadio2" value="2"> 2
        </label>
        <label class="radio-inline" style="margin-left:0.5cm">
          <input type="radio" name="grammar" id="inlineRadio3" value="3"> 3
        </label>
        <label class="radio-inline" style="margin-left:0.5cm">
          <input type="radio" name="grammar" id="inlineRadio4" value="4" checked> 4
        </label>
        <label class="radio-inline" style="margin-left:0.5cm">
          <input type="radio" name="grammar" id="inlineRadio5" value="5"> 5
        </label>
        <label class="radio-inline" style="margin-left:0.5cm">
          <input type="radio" name="grammar" id="inlineRadio6" value="6"> 6
        </label>
        <label class="radio-inline" style="margin-left:0.5cm">
          <input type="radio" name="grammar" id="inlineRadio7" value="7"> 7
        </label>
        <label class="radio-inline" style="margin-left:0.5cm">
          <strong>Very Good</strong>
        </label>
      </div>
      <span class="form-text text-muted">Is the text grammatical (no spelling or grammatical errors)?</span>
    </div>
    <br>
    <div class="form-group">
      <label>Clarity</label>
      <div class="radio">
        <label class="radio-inline">
          <strong>Very Bad</strong>
        </label>
        <label class="radio-inline" style="margin-left:0.5cm">
          <input type="radio" name="clarity" id="inlineRadio1" value="1"> 1
        </label>
        <label class="radio-inline" style="margin-left:0.5cm">
          <input type="radio" name="clarity" id="inlineRadio2" value="2"> 2
        </label>
        <label class="radio-inline" style="margin-left:0.5cm">
          <input type="radio" name="clarity" id="inlineRadio3" value="3"> 3
        </label>
        <label class="radio-inline" style="margin-left:0.5cm">
          <input type="radio" name="clarity" id="inlineRadio4" value="4" checked> 4
        </label>
        <label class="radio-inline" style="margin-left:0.5cm">
          <input type="radio" name="clarity" id="inlineRadio5" value="5"> 5
        </label>
        <label class="radio-inline" style="margin-left:0.5cm">
          <input type="radio" name="clarity" id="inlineRadio6" value="6"> 6
        </label>
        <label class="radio-inline" style="margin-left:0.5cm">
          <input type="radio" name="clarity" id="inlineRadio7" value="7"> 7
        </label>
        <label class="radio-inline" style="margin-left:0.5cm">
          <strong>Very Good</strong>
        </label>
      </div>
      <span class="form-text text-muted">Does the text clearly express the data?</span>
    </div>
    <div class="form-group">
      <input type="hidden" name="url" value="19073.php" />
      <button id="button" class="btn btn-primary">Submit</button>
      <span id="timer" class="form-text text-muted">00:20</span>
    </div>
  </form>
</footer>
</body>
</html>