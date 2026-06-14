import axios from "axios";

export interface SendGridNotificationPayload {
  to: string;
  subject: string;
  html: string;
  text?: string;
}

export interface SendGridResponse {
  success: boolean;
  messageId?: string;
  error?: string;
}

/**
 * NotificationService - Integrated with SendGrid
 * Sends system alerts, user notifications, and admin alerts
 */
export class NotificationService {
  private static apiKey = process.env.SENDGRID_API_KEY;
  private static apiUrl = "https://api.sendgrid.com/v3/mail/send";

  /**
   * Send a notification email via SendGrid
   */
  static async sendEmail(
    payload: SendGridNotificationPayload
  ): Promise<SendGridResponse> {
    if (!this.apiKey) {
      return {
        success: false,
        error: "SendGrid API key not configured",
      };
    }

    try {
      const response = await axios.post(
        this.apiUrl,
        {
          personalizations: [
            {
              to: [{ email: payload.to }],
              subject: payload.subject,
            },
          ],
          from: {
            email: process.env.SENDGRID_FROM_EMAIL || "noreply@aeis.dev",
            name: "AEIS System",
          },
          content: [
            {
              type: "text/html",
              value: payload.html,
            },
            ...(payload.text
              ? [
                  {
                    type: "text/plain",
                    value: payload.text,
                  },
                ]
              : []),
          ],
        },
        {
          headers: {
            Authorization: `Bearer ${this.apiKey}`,
            "Content-Type": "application/json",
          },
        }
      );

      return {
        success: true,
        messageId: response.headers["x-message-id"],
      };
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Unknown error";
      return {
        success: false,
        error: errorMessage,
      };
    }
  }

  /**
   * Send knowledge ingestion notification
   */
  static async notifyKnowledgeIngestion(
    adminEmail: string,
    conceptLabel: string,
    status: "success" | "failed"
  ): Promise<SendGridResponse> {
    const html =
      status === "success"
        ? `<p>Knowledge concept "<strong>${conceptLabel}</strong>" has been successfully ingested into AEIS.</p>`
        : `<p>Failed to ingest knowledge concept "<strong>${conceptLabel}</strong>". Please check the logs.</p>`;

    return this.sendEmail({
      to: adminEmail,
      subject: `Knowledge Ingestion ${status === "success" ? "Successful" : "Failed"}: ${conceptLabel}`,
      html,
      text: html,
    });
  }

  /**
   * Send prerequisite conflict alert
   */
  static async notifyPrerequisiteConflict(
    userEmail: string,
    conceptLabel: string,
    blockedBy: string[]
  ): Promise<SendGridResponse> {
    const html = `
      <p>Hi,</p>
      <p>You attempted to access "<strong>${conceptLabel}</strong>" but it requires these prerequisites:</p>
      <ul>
        ${blockedBy.map((item) => `<li>${item}</li>`).join("")}
      </ul>
      <p>Please complete the prerequisites first.</p>
    `;

    return this.sendEmail({
      to: userEmail,
      subject: `Prerequisites Required for ${conceptLabel}`,
      html,
    });
  }

  /**
   * Send system alert to admins
   */
  static async sendSystemAlert(
    adminEmails: string[],
    alertTitle: string,
    alertBody: string
  ): Promise<SendGridResponse[]> {
    const promises = adminEmails.map((email) =>
      this.sendEmail({
        to: email,
        subject: `[AEIS Alert] ${alertTitle}`,
        html: `<p><strong>${alertTitle}</strong></p><p>${alertBody}</p>`,
      })
    );

    return Promise.all(promises);
  }
}
