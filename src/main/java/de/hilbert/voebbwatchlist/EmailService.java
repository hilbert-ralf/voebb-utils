package de.hilbert.voebbwatchlist;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.stereotype.Service;

@Service
@Slf4j
public class EmailService {

    @Autowired
    private JavaMailSender emailSender;

    @Value("${app.mail.delivery.recipients}")
    private String[] MAIL_RECIPIENTS;

    @Value("${spring.mail.username}")
    private String MAIL_SENDER;

    public void sendSimpleMessage(String mailContent) {
        log.info("sending message of {} bytes to {}", mailContent.getBytes().length, MAIL_RECIPIENTS);
        SimpleMailMessage message = new SimpleMailMessage();
        message.setFrom(MAIL_SENDER);
        message.setTo(MAIL_RECIPIENTS);
        message.setSubject("Verfügbarkeiten deiner VÖBB Wunschliste");
        message.setText(mailContent);
        emailSender.send(message);
    }
}
