UPDATE hipeac_event
SET image = CONCAT('public/images/18/', id, '.jpg')
WHERE id IN (
	6779, 6783, 6785, 6787, 6790, 6791, 6792, 6793, 6794, 6795, 6796
)


UPDATE hipeac_event
SET redirect_url = CONCAT('http://old.hipeac.net/hipeac', YEAR(start_date))
WHERE id IN (
	1, 2, 6, 7, 10, 12, 14, 16, 6780
)


UPDATE hipeac_event
SET redirect_url = CONCAT('http://acaces.hipeac.net/', YEAR(start_date), '/')
WHERE id > 25 and id < 40


INSERT INTO `django_flatpage` (`id`, `url`, `title`, `content`, `enable_comments`, `template_name`, `registration_required`)
VALUES
	(1, '/privacy-policy/', 'Privacy policy', '**General**\n\nWe appreciate your interest in our website. For external links to external content, we assume, despite careful control, no liability.\n\nThe protection of your personal data when collecting, processing and use during your visit to our website is important to us.\n\nYour personal data are processed by us only in accordance with the provisions of German data privacy laws. The following provisions describe the type, scope and purpose of collecting, processing and utilizing personal data. This data privacy policy applies only to our web pages. If links on our pages route you to other pages, please inquire there about how your data are handled in such cases.\n\n**Inventory data**\n\n(1) Your personal data, insofar as these are necessary for this contractual relationship (inventory data) in terms of its establishment, organization of content and modifications, are used exclusively for fulfilling the contract. For goods to be delivered, for instance, your name and address must be relayed to the supplier of the goods.\n\n(2) Without your explicit consent or a legal basis, your personal data are not passed on to third parties outside the scope of fulfilling this contract. After completion of the contract, your data are blocked against further use. After expiry of deadlines as per tax-related and commercial regulations, these data are deleted unless you have expressly consented to their further use.\n\n**Information about cookies**\n\n(1) To optimize our web presence, we might use cookies. These are small text files stored in your computer\'s main memory. These cookies are deleted after you close the browser. Other cookies remain on your computer (long-term cookies) and permit its recognition on your next visit. This allows us to improve your access to our site.\n\n(2) You can prevent storage of cookies by choosing a \"disable cookies\" option in your browser settings. Please notice that this might limit the functionality of our web pages as a result.\n\n**Disclosure**\n\nAccording to the Federal Data Protection Act, you have a right to free-of-charge information about your stored data, and possibly entitlement to correction, blocking or deletion of such data upon written request.', 0, 'flatpages/legal.html', 0),
	(2, '/disclaimer/', 'Disclaimer', 'If you provide personal data via this website, these will be processed in compliance with the Data Protection Act of North Rhine-Westphalia (DSG NRW). RWTH Aachen University has appointed a data protection officer who is responsible for administering the Act and who advises on the respective duties.\n\n**Contact**\n\n_[Data Protection Officer](http://www.rwth-aachen.de/go/id/bdfr/contact/aaaaaaaaaaacetj/gguid/0x4AE08AA3CF31D611BDB90002A5871170/lidx/1)_  \nPhone: +49 241 80 93665  \nEmail: [dsb@rwth-aachen.de](mailto:dsb@rwth-aachen.de)\n\n**Collection, Processing and Use of Personal Data**\n\nOn principle, you can use our website without revealing your identity. By sending any information to RWTH (through a contact form, for example) you consent to this information being processed for our own purposes (e.g. sending of desired information, processing for advertising or for market opinion research) unless you declared an objection. You have the right to withdraw your consent at any time in the future, to immediate effect.\n\nUpon a visit to our website the following data will be stored exclusively for statistical purposes, and the identity of the user is being kept anonymous:\n\n - the name of the file requested\n - the date and time of the request\n - the amount of data transferred\n - IP number\n\nWe will not give any stored data to third parties – neither for commercial nor non-commercial purposes.\n\n**Responsibility for our Web Content**\n\nRWTH Aachen University makes all reasonable efforts to ensure that the contents of its web site are up-to-date, complete and accurate. Despite these efforts, the occurrence of errors or omissions cannot be completely ruled out.\n\nAs a provider of teleservices and media services we are responsible only for own contents according to § 7 of the German Telemedia Act (TMG). RWTH Aachen University does not accept liability for the relevance, accuracy or completeness of the content provided on its web site unless the error or inaccuracy occurred intentionally or through gross negligence. This refers to any loss, additional costs or damage of any kind suffered as a result of the use of material provided by this web site.\n\n**Responsibility for External Content**\n\nSome hyperlinks on this website link to contents which are not operated by RWTH but provided by third parties. Please note that RWTH Aachen University is not responsible for contents offered by other organisations.\n\n**Copyright**\n\nThe Layout of the Homepage, graphics and pictures used and the collection of individual contributions are protected by copyright.\n\nThe RWTH reserves all rights including the rights of photomechanical reproduction, the duplication and distribution via special processes (e.g. data processing, data carriers, data networks).\n\n**Any Questions?**\n\nIf you have any questions concerning the processing of your personal data, please contact our data protection officer who will be glad to assist you with your query.\n\n**Legal Validity**\n\nThis general disclaimer is part of the contents provided by the web site of RWTH Aachen University. If any of the terms and conditions is found to be invalid by reason of the relevant laws then the remaining terms and conditions shall remain in full effect.', 0, 'flatpages/legal.html', 0),
	(3, '/events/', 'HiPEAC Events', 'HiPEAC organizes four networking events per year: the HiPEAC Conference, two Computing Systems Weeks and a Summer School.', 0, 'events/events.html', 0),
	(4, '/vision/', 'HiPEAC Vision', 'Every couple of years we work on the HiPEAC Vision on high-performance embedded architecture and compilation for the coming decade.', 0, 'vision/vision.html', 0),
	(5, '/jobs/', 'HiPEAC Jobs', 'HiPEAC Jobs is a service offered by the HiPEAC Network to bring together recruiters (companies large and small, universities and research centres) with the skilled researchers that they need.', 0, 'recruitment/jobs.html', 0),
	(6, '/news/', 'HiPEAC News', '-', 0, 'communication/news.html', 0),
	(7, '/press/', 'Press room', '-', 0, 'communication/press.html', 0),
	(8, '/network/', 'HiPEAC Network', 'Since 2004, the HiPEAC project has provided a hub for European researchers and industry representatives in computing systems.', 0, 'network/network.html', 0);


INSERT INTO `django_flatpage_sites` (`id`, `flatpage_id`, `site_id`)
VALUES
	(1, 1, 1),
	(2, 2, 1),
	(3, 3, 1),
	(4, 4, 1),
	(5, 5, 1),
	(6, 6, 1),
	(7, 7, 1),
	(8, 8, 1);


INSERT INTO `hipeac_page` (`flatpage_ptr_id`)
VALUES
	(3),
	(4),
	(5),
	(6),
	(7),
	(8);


INSERT INTO `hipeac_block` (`id`, `key`, `notes`, `header`, `content`, `page_id`)
VALUES
	(1, 'about', 'Main header is taken from the parent page.', 'HiPEAC organizes four networking events per year: the HiPEAC Conference, two Computing Systems Weeks and a Summer School.', 'Collaboration and networking between member institutions and across the different disciplines: computer architects, design tool builders, compiler builders, system designers, between researchers from academia and industry, between European and non-European institutions. This collaboration between best of breed must lead to more European excellence in the HiPEAC domain. Collaboration and networking is stimulated by means of the various networking events, and the small collaboration incentives like collaboration grants, mini-sabbaticals, internships,...', 3),
	(2, 'csw', '-', 'In the spring and autumn, the HiPEAC community gets together at Computing Systems Weeks. Unified by a central theme, these events enable you to host a workshop or tutorial, present products or services, or pitch your organization to local students.', 'As with all HiPEAC events, they offer an excellent opportunity to network with leading representatives of the global computing systems community.', 3),
	(3, 'conference', '-', 'The HiPEAC conference provides a high-quality forum for computer architects and compiler builders working in the field of high performance computer architecture and compilation for embedded systems, but is also open to general-purpose research which is becoming increasingly relevant to the embedded domain.', 'The conference aims at the dissemination of advanced scientific knowledge and the promotion of international contacts among scientists from academia and industry. Topics of interest include, but are not limited to:\n\n- Processor architectures\n- Memory system optimization\n- Power, performance and implementation efficient designs\n- Interconnection networks, networks-on-chip, network interfaces and processors\n- Security, dependability, and predictability support\n- Application specific processors and accelerators\n- Reconfigurable architectures\n- Simulation and methodology\n- Compiler techniques for embedded processors\n- Feedback-directed optimization\n- Program characterization and analysis techniques\n- Dynamic compilation, adaptive execution, and continuous profiling/optimization\n- Back-end code generation\n- Binary translation/optimization\n- Code size/memory footprint optimizations', 3),
	(4, 'acaces', '-', 'ACACES, the \"HiPEAC Summer School\", is a one week summer school for computer architects and compiler builders working in the field of high performance computer architecture and compilation for embedded systems.', 'The school aims at the dissemination of advanced scientific knowledge and the promotion of international contacts among scientists from academia and industry. A distinguishing feature of this Summer School is its broad scope ranging from low level technological issues to advanced compilation techniques. In the design of modern computer systems one has to be knowledgeable about architecture as well as about the quality of the code, and how to improve it. This summer school offers the ideal mix of the two worlds – both at the entry level and at the most advanced level. The ACACES Summer School is organized by HiPEAC. The summer school is open to everybody but previous training and/or experience in computer science as well as a background in computer architecture or compilation is indispensable.', 3),
	(8, 'about', 'Main header is taken from the parent page.', 'HiPEAC Jobs is a service offered by the HiPEAC Network to bring together recruiters (companies large and small, universities and research centres) with the skilled researchers that they need.', 'HiPEAC Jobs is targeted to **computing systems professionals**. Recruiters can have confidence that their vacancy advertisements will get attention from qualified candidates with skills aligned to their business needs. Candidates can take advantage of a job portal dedicated to computing systems offering the ability to filter vacancies by core skill, location or career stage.', 5),
	(9, 'about_recruiters', '-', 'How does it work for recruiters?', '- Log in to the HiPEAC website, go to the Jobs page and click on ‘Add a new job/internship’. Fill in a simple form with the details of your Europe-based computing systems vacancy and your job will be advertised on the portal after a quick check by a member of our team.\r\n\r\n- Non HiPEAC members just need to create an account on the HiPEAC website, which is quick, easy and costs nothing.\r\n\r\n- Your vacancies are made visible to thousands of computing systems researchers, doctoral students and professionals across the world through the portal and via our mailing lists, social media, events and newsletters. Vacancies are advertised:\r\n    - On the jobs portal [hipeac.net/jobs](https://www.hipeac.net/jobs/)\r\n    - Via the [HiPEAC Jobs Twitter](https://twitter.com/hipeacjobs)\r\n    - Via the [HiPEAC LinkedIn page](https://www.linkedin.com/company/hipeac)\r\n    - Via a regular jobs e-bulletin to network members and hundreds of other individuals\r\n    - To the wider HiPEAC community via links to the jobs portal in the HiPEACInfo quarterly newsletter and our four well-attended annual international events\r\n\r\n- Vacancy adverts are automatically removed from the jobs portal when the application deadline passes.', 5),
	(10, 'about_students', '-', 'How does it work for candidates?', '- Just go to the portal and browse all vacancies or use the filters to search for roles according to location, area of technical expertise or career level.\r\n\r\n- View vacancies relevant to your skills in both industrial and academic organisations and discover which organisations recruit in particular fields of expertise.\r\n\r\n- No need to create usernames or accounts; click on the vacancy advert to apply directly to the recruiter.', 5),
	(11, 'magazine', '-', 'The HiPEAC Newsletter is a quarterly publication providing the latest news on the activities within the European HiPEAC network, as well as activities on high-performance embedded architectures and compilers at large.', 'The Newsletter is sent to more than 500 researchers from academia and industry, and company managers in Europe, America and Asia.', 6),
	(12, 'about', 'Main header is taken from the parent page.', 'Since 2004, the HiPEAC (High Performance and Embedded Architecture and Compilation) project has provided a hub for European researchers and industry representatives in computing systems; today, its network, the biggest of its kind in the world, numbers almost 2,000 specialists. It provides a platform for cross-disciplinary research collaboration, brings together representatives from research, industry and policy, and helps prepare the next generation of world-class computer scientists.', 'HiPEAC organizes four networking events per year: the HiPEAC conference, two Computing Systems Weeks and a summer school. It also produces the biennial HiPEAC Vision, an influential roadmap which informs European technology research policy areas. In addition, the project offers training, support for academic and industry placements, help in finding excellent computing candidates, careers activities and dissemination support.', 8),
	(13, 'about_industry', '', 'For industry', 'By participating in HiPEAC, industry members gain access to over 800 PhD students with the specialist skills needed for a wide range of computing roles. They can form partnerships with researchers and get access to the latest research developments, as well as influencing the direction of computing systems research through the HiPEAC Vision and European Commission concertation meetings.', 8),
	(14, 'about_researchers', '', 'For researchers', 'Participating in HiPEAC allows academic members to collaborate across disciplines and find partners for research projects or business ventures, as well as attracting new students to their areas of study. It allows them professional development opportunities and gives them greater visibility.', 8),
	(15, 'about_projects', '', 'For projects', 'HiPEAC helps European Commission-funded project leaders recruit the specialist staff they need to carry out their research. It provides numerous opportunities for the dissemination of project results and helps projects gain greater visibility in the research community while giving them exposure to industry representatives and potential future investors.', 8),
	(17, 'about_students', '', 'For students', 'HiPEAC provides grants for industrial and academic placements, and opportunities to learn from the best computing professors in the world. It is an incubator for the next generation of computing systems talent.', 8),
	(18, 'about_innovation', '', 'For innovators', 'HiPEAC allows innovation specialists access to a large network of highly specialized researchers, as well as making them the first to find out about research results which could be turned into disruptive products or services.', 8),
	(19, 'roadshow', '-', 'Every year, HiPEAC participates in external events, giving the HiPEAC community the chance to share their research findings, new products and services, or job openings with new audiences.', 'From trade shows to job fairs, the HiPEAC roadshow offers you numerous opportunities to spread the word about your work. If you\'re participating in a European project, you can disseminate results without the expense or administrative burden of booking a booth yourself. The travelling HiPEAC jobs wall, meanwhile, means that your job vacancies uploaded to the [HiPEAC Jobs portal](/jobs/) will be browsed by computing systems experts throughout Europe. \n\nFor further information about our current programme, and to participate in the roadshow, email: [communication@hipeac.net](mailto:communication@hipeac.net).', 3),
	(20, 'about_team_coordinator', 'Avatar should be an square image.', 'Koen De Booschere', 'Contact for: general information on the network.', 8),
	(21, 'about_team_management', 'Avatar should be an square image.', 'Vicky Wandels', 'Contact for: finances, registration and organisation of activities, administrative issues, meetings.', 8),
	(22, 'about_team_recruitment', 'Avatar should be an square image.', 'Xavi Salazar', 'Contact for: recruitment activities.', 8),
	(23, 'about_team_communication', 'Avatar should be an square image.', 'Madeleine Gray', 'Contact for: communication, newsletter, HiPEAC related projects, organisation of activities.', 8),
	(24, 'about_team_tech', 'Avatar should be an square image.', 'Eneko Illarramendi', 'Contact for: server issues, website issues and suggestions, mailing lists, newsletter, organisation of activities.', 8),
	(25, 'industry_benefits', 'Custom icons can be used: <icon name=\"lock\"></icon>', 'Membership benefits', '- <icon name=\"how_to_reg\"></icon>Find highly qualified, specialist staff and interns\r\n- <icon name=\"euro_symbol\"></icon>Get funding for internships (small/medium enterprises only)\r\n- <icon name=\"search\"></icon>Gain insight into the latest high-performance and embedded systems trends\r\n- <icon name=\"memory\"></icon>Grow your technology user base or ecosystem\r\n- <icon name=\"person_add\"></icon>Gain visibility and meet new clients\r\n- <icon name=\"star\"></icon>Influence European Union work programmes and strategic agendas', 8),
	(26, 'industry_get_involved', '', 'Get involved', '- Advertise vacancies on hipeac.net/jobs\n- Submit an internship proposal\n- Pitch your company at a careers event\n- Showcase your products and services at the HiPEAC conference industry exhibition\n- Participate in the HiPEAC Industry Partnership Programme\n- Sponsor the HiPEAC conference\n- Send your input to the HiPEAC Vision\n- Feature your business in the HiPEAC magazine', 8),
	(27, 'innovation_benefits', 'Custom icons can be used: <icon name=\"lock\"></icon>', 'Membership benefits', '- <icon name=\"accessibility_new\"></icon>Build partnerships with the researchers creating the computing systems of tomorrow\n- <icon name=\"wb_incandescent\"></icon>Be the first to find out about research results which might be the next big technology trend\n- <icon name=\"how_to_reg\"></icon>Find highly qualified, specialist staff and interns\n- <icon name=\"memory\"></icon>Grow your technology user base or ecosystem\n- <icon name=\"star\"></icon>Influence European Union work programmes and strategic agendas', 8),
	(28, 'innovation_get_involved', '', 'Get involved', '- Advertise vacancies on hipeac.net/jobs\n- Submit an internship proposal\n- Host a workshop at the HiPEAC conference or Computing Systems Week\n- Submit an entry for the HiPEAC Technology Transfer Awards\n- Showcase your technologies and services at the HiPEAC conference industry exhibition\n- Sponsor the HiPEAC conference\n- Send your input for the HiPEAC Vision\n- Contribute to the HiPEAC magazine', 8),
	(29, 'students_benefits', 'Custom icons can be used: <icon name=\"lock\"></icon>', 'Membership benefits', '- <icon name=\"touch_app\"></icon>Use HiPEAC Jobs to find the most interesting career opportunities in computing systems\n- <icon name=\"how_to_reg\"></icon>Get careers advice and job information from top companies and research institutes\n- <icon name=\"flight_takeoff\"></icon>Help your career take off with a funded international internship\n- <icon name=\"pageview\"></icon>Learn from the most renowned computing systems researchers in Europe\n- <icon name=\"developer_board\"></icon>Find out about the latest computing systems research\n- <icon name=\"record_voice_over\"></icon>Publicize your thesis to the computing systems community', 8),
	(30, 'students_get_involved', '', 'Get involved', '- Search the latest career opportunities on hipeac.net/jobs\n- Apply for a funded internship at a top international company or innovative start-up\n- Attend HiPEAC’s annual summer school, ACACES\n- Participate in the STEM student day at the HiPEAC conference\n- Take part in a Student Heterogeneous Programming Challenge and Inspiring Futures careers session at Computing Systems Week\n- Attend the HiPEAC conference , including keynote speeches by renowned scientists\n- Publish your ‘three-minute thesis’ or internship report in the HiPEAC magazine', 8),
	(31, 'researchers_benefits', 'Custom icons can be used: <icon name=\"lock\"></icon>', 'Membership benefits', '- <icon name=\"accessibility_new\"></icon>Build partnerships and form project consortia with computing systems researchers all over Europe\r\n- <icon name=\"how_to_reg\"></icon>Find highly qualified, specialist staff and interns\r\n- <icon name=\"search\"></icon>Learn about the latest computing systems research\r\n- <icon name=\"record_voice_over\"></icon>Gain greater visibility for your research\r\n- <icon name=\"memory\"></icon>Grow your technology user base or ecosystem\r\n- <icon name=\"wb_incandescent\"></icon>Transform your research results into market-ready innovations\r\n- <icon name=\"star\"></icon>Find out about the latest policy directions and influence European Union work programmes and strategic agendas', 8),
	(32, 'researchers_get_involved', '', 'Get involved', '- Advertise vacancies for your team on hipeac.net/jobs\n- Organize a workshop at the HiPEAC conference or Computing Systems Week\n- Attend the HiPEAC conference and participate in the exhibition\n- Attend HiPEAC’s annual summer school, ACACES – or send your students\n- Participate in an Inspiring Futures careers event\n- Contribute to the HiPEAC Vision\n- Contribute to the HiPEAC magazine', 8),
    (33, 'projects_benefits', 'Custom icons can be used: <icon name=\"lock\"></icon>', 'Membership benefits', '- <icon name=\"device_hub\"></icon>Build partnerships and form project consortia with computing systems researchers all over Europe\n- <icon name=\"how_to_reg\"></icon>Find specialist staff and interns qualified in the right technology for your project\n- <icon name=\"record_voice_over\"></icon>Meet your project dissemination objectives through activities organized by HiPEAC\n- <icon name=\"important_devices\"></icon>Take advantage of HiPEAC’s ready-made hub for project meetings\n- <icon name=\"memory\"></icon>Grow your technology user base or ecosystem\n- <icon name=\"star\"></icon>Influence European Union work programmes and strategic agendas', 8),
	(34, 'projects_get_involved', '', 'Get involved', '- Advertise project vacancies on hipeac.net/jobs\n- Submit an internship proposal\n- Organize a workshop at the HiPEAC conference or Computing Systems Week\n- Showcase project at the HiPEAC conference exhibition\n- Present your project at a HiPEAC roadshow event\n- Contribute to the HiPEAC magazine', 8);
