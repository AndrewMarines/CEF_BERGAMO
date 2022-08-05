<head>
</head>
<body>
<?php
	$servername = "localhost";
	$username = "root";
	$password = "SestanteA";
	$dbname = "cef_bergamo";

	// Create connection
	$conn = new mysqli($servername, $username, $password, $dbname);
	// Check connection
	if ($conn->connect_error) {
	  die("Connection failed: " . $conn->connect_error);
	}

	
   if(isset($_POST['submit'])) {
	$peso = $_POST['modal-peso'];
	$id = $_POST['id_singolo'];
	$targa = $_POST['modal-targa'];
	
	$sql = "UPDATE pesate SET pesata='$peso' WHERE id='$id'";

	if ($conn->query($sql) === TRUE) {
	  echo "Record updated successfully";
	} else {
	  echo "Error updating record: " . $conn->error;
	}
		
	$sql = "SELECT id FROM targhe WHERE targa = '$targa'";
	$result = $conn->query($sql) ;
	if($result && $result->num_rows>0){
		$row = $result->fetch_assoc();
		$id_targa = $row['id'];
	
	}
	
	$sql = "UPDATE pesate SET id_targa=$id_targa WHERE id=$id";

	if ($conn->query($sql) === TRUE) {
	  echo "Record updated successfully";
	} else {
	  echo "Error updating record: " . $conn->error;
	}

	$conn->close();
	
   }


?>
</body>


