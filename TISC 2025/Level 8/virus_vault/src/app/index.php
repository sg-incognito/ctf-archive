<?php

class Virus
{
    public $name;
    public $species;
    public $valid_species = ["Ghostroot", "IronHydra", "DarkFurnace", "Voltspike"];

    public function __construct(string $name, string $species)
    {
        $this->name = $name;
        $this->species = in_array($species, $this->valid_species) ? $species : throw new Exception("That virus is too dangerous to store here: " . htmlspecialchars($species));
    }

    public function printInfo()
    {
        echo "Name: " . htmlspecialchars($this->name) . "<br>";
        include $this->species . ".txt";
    }
} 

class VirusVault
{
    private $pdo;

    public function __construct(string $conn)
    {
        $this->pdo = new PDO($conn);
        $this->pdo->query("CREATE TABLE IF NOT EXISTS virus_vault (id INTEGER PRIMARY KEY AUTOINCREMENT, virus TEXT NOT NULL);");
    }

    public function storeVirus(Virus $virus)
    {
        $ser = serialize($virus);
        $quoted = $this->pdo->quote($ser);
        $encoded = mb_convert_encoding($quoted, 'UTF-8', 'ISO-8859-1');
        if (!empty($_GET['debug'])) {
            echo "<pre>---- DEBUG STORE ----\n";
            echo "serialized (raw):\n" . htmlspecialchars($ser) . "\n\n";
            echo "serialized (hex):\n" . bin2hex($ser) . "\n\n";

            echo "quoted (raw):\n" . htmlspecialchars($quoted) . "\n\n";
            echo "quoted (hex):\n" . bin2hex($quoted) . "\n\n";

            echo "encoded (raw):\n" . htmlspecialchars($encoded) . "\n\n";
            echo "encoded (hex):\n" . bin2hex($encoded) . "\n\n";

            // compute inner encoded substring (strip surrounding single or double quote if present)
            $inner = $encoded;
            if (strlen($inner) >= 2) {
                $first = substr($inner, 0, 1);
                $last  = substr($inner, -1);
                if (($first === "'" || $first === '"') && $last === $first) {
                    $inner = substr($inner, 1, -1);
                }
            }

            // lengths and hex info
            $ser_len   = strlen($ser);
            $quoted_len= strlen($quoted);
            $enc_len   = strlen($encoded);
            $inner_len = strlen($inner);

            echo "lengths (bytes):\n";
            echo "  serialized length: " . $ser_len . "\n";
            echo "  quoted length   : " . $quoted_len . "\n";
            echo "  encoded length  : " . $enc_len . "  (includes surrounding quotes if present)\n";
            echo "  encoded inner length: " . $inner_len . "  <-- use this value for payload sizing\n\n";

            echo "encoded inner (hex):\n" . bin2hex($inner) . "\n";
            echo "---------------------</pre>";
            // // flush so output appears immediately
            // if (function_exists('fastcgi_finish_request')) {
            //     @fastcgi_finish_request();
            // } else {
            //     @flush();
            //     @ob_flush();
            // }
        }

        try {
            $sql = "INSERT INTO virus_vault (virus) VALUES ($encoded)";
            if (!empty($_GET['debug'])) {
                echo "<pre>---- DEBUG SQL ----\n";
                echo $sql . "\n";
                echo "-------------------</pre>";
            }
            $this->pdo->query($sql);
            echo "Query done.";
            return $this->pdo->lastInsertId();
        } catch (Exception $e) {
            echo "ERROR INSERTING!";
            throw new Exception("An error occured while locking away the dangerous virus!");
        }
    }

    public function fetchVirus(string $id)
    {
        try {
            $quoted = $this->pdo->quote(intval($id));

            $result = $this->pdo->query("SELECT virus FROM virus_vault WHERE id == $quoted");

            // Debug output for fetch ID quoting (enable with &debug=1)
            if (!empty($_GET['debug'])) {
                echo "<pre>---- DEBUG FETCH 1 ----\n";
                echo "Result (type): " . gettype($result) . "\n\n";
                echo "Result (export):\n" . htmlspecialchars(var_export($result, true)) . "\n\n";
                echo "---------------------</pre>";
            }


            if ($result !== false) {
                $row = $result->fetch(PDO::FETCH_ASSOC);
                // Debug output for fetch ID quoting (enable with &debug=1)
                if (!empty($_GET['debug'])) {
                    echo "<pre>---- DEBUG FETCH 2 ----\n";
                    echo "Row (export):\n" . htmlspecialchars(print_r($row, true)) . "\n\n";
                    echo "---------------------</pre>";
                }
                if ($row && isset($row['virus'])) {
                    return unserialize($row['virus']);
                }
            }
            return null;
        } catch (Exception $e) {
            echo "An error occured while fetching your virus... Run!";
            print_r($e);
        }
        return null;
    }
}

session_start();
$storage = new VirusVault("sqlite:/tmp/virus_" . session_id() . '.db');

ini_set("open_basedir", getcwd());
$id = $_GET["id"] ?? "";
$name = $_GET["name"] ?? "";
$action = $_GET["action"] ?? "";
$species = $_GET["species"] ?? "";

try {
    switch ($action) {
        case "store":
            $virus = new Virus($name, $species);
            $id =  $storage->storeVirus($virus);
            $output = "Successfully quarantined '" . htmlspecialchars($name) . "'. Your virus sample ID is " . $id . ".";
            break;
        case "fetch":
            $fetched = $storage->fetchVirus($id);
            
            if (is_null($fetched)) {
                $output = "Unfortunately, we could not find any virus with the sample ID '" . htmlspecialchars($id) . "' in our records.";
            } elseif($fetched instanceof Virus) {
                ob_start();
                echo "Your virus sample was found. Handle it with care!<br><br>";
                $fetched->printInfo();
                $output = ob_get_clean();
            } else {
                $output = "We found your virus but it was... corrupted?!";
            }

            // Print some debug information about the fetched data
            if (!empty($_GET['debug'])) {
                echo "<pre>---- DEBUG PRINT ----\n";
                echo "fetched (raw):\n" . htmlspecialchars(var_export($fetched, true)) . "\n\n";
                echo "fetched (hex):\n" . bin2hex(var_export($fetched, true)) . "\n";
                echo "---------------------</pre>";
            }

            break;
        default:
            $output = "We hope you have a pleasant day at the Virus Vault™";
    }
} catch (Exception $e) {
    $output = $e->getMessage();
}

$html = file_get_contents("index.html");
$html = str_replace('{{output}}', $output, $html);
echo $html;
