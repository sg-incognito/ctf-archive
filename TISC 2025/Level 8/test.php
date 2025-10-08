<?php
$ser = 'O:5:"Virus":3:{s:4:"name";s:278:"éééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééééTest";s:7:"species";s:6:"Potato";s:13:"valid_species";a:4:{i:0;s:9:"Ghostroot";i:1;s:6:"Potato";i:2;s:11:"DarkFurnace";i:3;s:9:"Voltspike";}';

// extract declared length and inner bytes
if (preg_match('/s:(\d+):"(.*)";s:7:"species"/sU', $ser, $m)) {
    $decl = (int)$m[1];
    $inner = $m[2];
    echo "declared = $decl\n";
    echo "actual bytes = " . strlen($inner) . "\n";
} else {
    echo "failed to parse header\n";
}

// try unserialize safely (no class instantiation)
var_dump(@unserialize($ser, ['allowed_classes' => false]));
