<?php
// Read-only lookup: actual group IDs from this installation, never fixture IDs.
require '/var/www/html/vendor/autoload.php';
(new Symfony\Component\Dotenv\Dotenv())->bootEnv('/var/www/html/.env');
$kernel = new App\Kernel('prod', false);
$kernel->boot();
$em = $kernel->getContainer()->get('doctrine')->getManager();
$result = [];
foreach ($em->getRepository(App\Entity\UserSystem\Group::class)->findAll() as $group) {
    $result[$group->getName()] = $group->getID();
}
echo json_encode($result, JSON_THROW_ON_ERROR);
